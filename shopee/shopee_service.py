import requests
from returns.result import ResultE, Success
from returns.functions import raise_exception
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.curry import curry
from returns.converters import flatten
from netsuite.sales_order import sales_order, sales_order_service

from shopee import shopee, shopee_repo, auth_repo, order_repo
from netsuite.sales_order import sales_order_service
from netsuite.customer import customer, customer_repo
from netsuite.order import order_service
from db import bigquery
from telegram import telegram

_builder = sales_order_service.build(
    items_fn=lambda x: x["item_list"],
    item_sku_fn=lambda x: x["item_sku"],
    item_qty_fn=lambda x: x["model_quantity_purchased"],
    item_amt_fn=lambda x: x["model_discounted_price"],
    item_location=sales_order.SHOPEE_ECOMMERCE["location"],
    ecom=sales_order.SHOPEE_ECOMMERCE,
    memo_builder=lambda x: f"{x['order_sn']} - shopee",
    customer_builder=lambda _: customer_repo.add(customer.SHOPEE_CUSTOMER),
)


def _token_refresh_service(token: shopee.AccessToken) -> ResultE[shopee.AccessToken]:
    with requests.Session() as session:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )


def _auth_service() -> ResultE[shopee.RequestBuilder]:
    return (
        auth_repo.get_access_token()
        .bind(_token_refresh_service)
        .map(lambda x: x["access_token"])
        .map(lambda x: shopee_repo.build_shopee_request(x, "query"))
    )


@curry
def _get_orders_items(
    request_builder: shopee.RequestBuilder,
    create_time: int,
) -> ResultE[list[shopee.Order]]:
    with requests.Session() as session:
        return flow(
            create_time,
            shopee_repo.get_orders(session, request_builder),
            bind(shopee_repo.get_order_items(session, request_builder)),
            map_(lambda x: [i for i in x if i["create_time"] != create_time]),  # type: ignore
            bind(order_repo.update_max_created_at),
        )


def _get_items(request_builder: shopee.RequestBuilder):
    with requests.Session() as session:
        return flow(
            shopee_repo.get_item_list(session, request_builder)(),
            bind(shopee_repo.get_items_info(session, request_builder)),
        )


def _get_orders_service() -> ResultE[list[shopee.Order]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders_items),
            _auth_service().apply,
            order_repo.get_max_created_at().apply,
        )
    )


def ingest_orders_service():
    return _get_orders_service().bind(
        order_service.ingest(
            order_repo.create,  # type: ignore
            _builder,
            telegram.SHOPEE_CHANNEL,
        )
    )


def get_items_service():
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
