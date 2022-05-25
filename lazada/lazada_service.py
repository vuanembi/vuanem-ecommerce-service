from datetime import datetime

import requests
from returns.result import ResultE, Success
from returns.functions import raise_exception
from returns.iterables import Fold
from returns.pipeline import flow
from returns.pointfree import bind
from returns.curry import curry
from returns.converters import flatten

from common import utils
from common.seller import Seller
from lazada import lazada, lazada_repo, auth_repo, order_repo
from netsuite.order import order_service
from db import bigquery


def _token_refresh_service(seller: Seller) -> ResultE[lazada.AccessToken]:
    def _svc(token: lazada.AccessToken) -> ResultE[lazada.AccessToken]:
        with requests.Session() as session:
            return (
                auth_repo.refresh_token(session, token)
                .bind(auth_repo.update_access_token(seller))
                .lash(raise_exception)
            )

    return _svc


def _auth_service(seller: Seller) -> ResultE[lazada.AuthBuilder]:
    return (
        auth_repo.get_access_token(seller)
        .bind(utils.check_expired)  # type: ignore
        .lash(_token_refresh_service(seller))  # type: ignore
        .map(lazada_repo.get_auth_builder)  # type: ignore
    )


def _get_items(session: requests.Session, auth_builder: lazada.AuthBuilder):
    def _get(orders: list[lazada.Order]) -> ResultE[lazada.OrderItems]:
        return Fold.collect_all(
            [
                lazada_repo.get_order_item(session, auth_builder, order["order_id"])
                for order in orders
            ],
            Success(()),
        ).map(
            lambda items: [  # type: ignore
                {
                    **order,
                    "items": item,
                }
                for order, item in zip(orders, items)
            ]
        )

    return _get


@curry
def _get_orders_items(
    seller: Seller,
    auth_builder: lazada.AuthBuilder,
    created_after: datetime,
) -> ResultE[list[lazada.OrderItems]]:
    with requests.Session() as session:
        return flow(
            created_after,
            lazada_repo.get_orders(session, auth_builder),
            bind(_get_items(session, auth_builder)),
            bind(order_repo.update_max_created_at(seller)),
        )


def _get_orders_service(seller: Seller) -> ResultE[list[lazada.OrderItems]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders_items(seller)),
            _auth_service(seller).apply,
            order_repo.get_max_created_at(seller).apply,
        )
    )


def ingest_orders_service(seller: Seller) -> ResultE[dict[str, list[dict]]]:
    return _get_orders_service(seller).bind(
        order_service.ingest(
            order_repo.create(seller),
            seller.order_builder,
            seller.name,
            seller.chat_id,
        )
    )


def get_products_service(*args):
    def _get(auth_builder: lazada.AuthBuilder):
        with requests.Session() as session:
            return lazada_repo.get_products(session, auth_builder)()

    return flow(
        _auth_service(),
        bind(_get),
        bind(
            bigquery.load(
                "IP_3rdPartyEcommerce",
                "Lazada_Products",
                lazada.ProductsSchema,
            )
        ),
    )
