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
from lazada import lazada, lazada_repo, auth_repo, order_repo
from netsuite.customer import customer, customer_repo
from netsuite.sales_order import sales_order, sales_order_service
from netsuite.order import order_service
from telegram import telegram
from db import bigquery

_builder = sales_order_service.build(
    items_fn=lambda x: x["items"],
    item_sku_fn=lambda x: x["sku"],
    item_qty_fn=lambda _: 1,
    item_amt_fn=lambda x: x["paid_price"] + x["voucher_platform"],
    item_location=sales_order.LAZADA_ECOMMERCE["location"],
    ecom=sales_order.LAZADA_ECOMMERCE,
    memo_builder=lambda x: f"{x['order_id']} - lazada",
    customer_builder=lambda _: customer_repo.add(customer.LAZADA_CUSTOMER),
)


def _token_refresh_service(token: lazada.AccessToken) -> ResultE[lazada.AccessToken]:
    with requests.Session() as session:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )


def _auth_service() -> ResultE[lazada.AuthBuilder]:
    return (
        auth_repo.get_access_token()
        .bind(utils.check_expired)  # type: ignore
        .lash(_token_refresh_service)  # type: ignore
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
    auth_builder: lazada.AuthBuilder,
    created_after: datetime,
) -> ResultE[list[lazada.OrderItems]]:
    with requests.Session() as session:
        return flow(
            created_after,
            lazada_repo.get_orders(session, auth_builder),
            bind(_get_items(session, auth_builder)),
            bind(order_repo.update_max_created_at),
        )


def _get_orders_service() -> ResultE[list[lazada.OrderItems]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders_items),
            _auth_service().apply,
            order_repo.get_max_created_at().apply,
        )
    )


def ingets_orders_service() -> ResultE[dict[str, list[dict]]]:
    return _get_orders_service().bind(
        order_service.ingest(
            order_repo.create,
            _builder,
            telegram.LAZADA_CHANNEL,
        )
    )


def get_products_service():
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
