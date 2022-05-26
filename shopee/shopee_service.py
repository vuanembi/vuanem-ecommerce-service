import requests
from returns.result import ResultE, Success
from returns.functions import raise_exception
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.curry import curry
from returns.converters import flatten

from common.seller import Seller
from shopee import shopee, shopee_repo, auth_repo, order_repo
from netsuite.order import order_service
from db import bigquery


def _token_refresh_service(seller: Seller):
    def _svc(token: shopee.AccessToken) -> ResultE[shopee.AccessToken]:
        with requests.Session() as session:
            return (
                auth_repo.refresh_token(seller, session, token)
                .bind(auth_repo.update_access_token(seller))
                .lash(raise_exception)
            )

    return _svc


def _auth_service(seller: Seller) -> ResultE[shopee.RequestBuilder]:
    return (
        auth_repo.get_access_token(seller)
        .bind(_token_refresh_service(seller))
        .map(lambda x: x["access_token"])
        .map(lambda x: shopee_repo.build_shopee_request(seller, x, "query"))
    )


@curry
def _get_orders_items(
    seller: Seller,
    request_builder: shopee.RequestBuilder,
    create_time: int,
) -> ResultE[list[shopee.Order]]:
    with requests.Session() as session:
        return flow(
            create_time,
            shopee_repo.get_orders(session, request_builder),
            bind(shopee_repo.get_order_items(session, request_builder)),
            map_(lambda x: [i for i in x if i["create_time"] != create_time]),  # type: ignore
            bind(order_repo.update_max_created_at(seller)),
        )


def _get_items(request_builder: shopee.RequestBuilder):
    with requests.Session() as session:
        return flow(
            shopee_repo.get_item_list(session, request_builder)(),
            bind(shopee_repo.get_items_info(session, request_builder)),
        )


def _get_orders_service(seller: Seller) -> ResultE[list[shopee.Order]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders_items(seller)),
            _auth_service(seller).apply,
            order_repo.get_max_created_at(seller).apply,
        )
    )


def ingest_orders_service(seller: Seller):
    return _get_orders_service(seller).bind(
        order_service.ingest(
            order_repo.create(seller),
            seller.order_builder,
            seller.name,
            seller.chat_id,
        )
    )


def get_items_service(*args):
    return flow(
        _auth_service(),
        bind(_get_items),
        bind(
            bigquery.load(
                "IP_3rdPartyEcommerce",
                "Shopee_Items",
                shopee.ItemsSchema,
            )
        ),
    )
