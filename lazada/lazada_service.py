from typing import Any
from datetime import datetime

import requests
from returns.result import ResultE, Success, safe
from returns.functions import raise_exception
from returns.iterables import Fold
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.curry import curry
from returns.converters import flatten

from common import utils
from lazada import lazada, auth_repo, data_repo
from netsuite import netsuite, netsuite_service, prepare_repo
from telegram import message_service

_build_prepared_order = netsuite_service.build_prepared_order_service(
    items_fn=lambda x: x["items"],
    item_sku_fn=lambda x: x["sku"],
    item_qty_fn=lambda _: 1,
    item_amt_fn=lambda x: x["paid_price"] + x["voucher_platform"],
    item_location=netsuite.LAZADA_ECOMMERCE["location"],
    ecom=netsuite.LAZADA_ECOMMERCE,
    memo_builder=lambda x: f"lazada - {x['order_id']}",
    customer_builder=lambda x: prepare_repo.build_customer(netsuite.LAZADA_CUSTOMER),
)


def token_refresh_service(token: lazada.AccessToken) -> ResultE[lazada.AccessToken]:
    with requests.Session() as session:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )


def auth_service() -> ResultE[lazada.AuthBuilder]:
    return (
        auth_repo.get_access_token()
        .lash(raise_exception)
        .bind(utils.check_expired)  # type: ignore
        .lash(token_refresh_service)  # type: ignore
        .map(data_repo.get_auth_builder)  # type: ignore
    )


def _get_items(session: requests.Session, auth_builder: lazada.AuthBuilder):
    def _get(orders: list[lazada.Order]) -> ResultE[lazada.OrderItems]:
        return Fold.collect_all(
            [
                data_repo.get_order_item(session, auth_builder, order["order_id"])
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
def _get_orders(auth_builder: lazada.AuthBuilder, created_after: datetime):
    with requests.Session() as session:
        return flow(
            created_after,
            data_repo.get_orders(session, auth_builder),
            bind(_get_items(session, auth_builder)),
            # bind(data_repo.persist_max_created_at),
        )


def get_orders_service() -> ResultE[list[lazada.OrderItems]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders),
            auth_service().apply,
            data_repo.get_max_created_at().apply,
        )
    )


def _handle_order(order: lazada.OrderItems):
    return flow(
        order,
        data_repo.persist_order,
        bind(_build_prepared_order),
        bind(prepare_repo.persist_prepared_order),
        map_(lambda x: x.id),  # type: ignore
    )


def order_service(orders: list[lazada.OrderItems]) -> ResultE[dict]:
    orders = orders[:2]
    return Fold.collect_all(
        [
            prepared_id.apply(
                order.apply(Success(message_service.send_new_order("Lazada")))
            )
            for order, prepared_id in [
                (Success(order), _handle_order(order)) for order in orders
            ]
        ],
        Success(()),
    ).map(lambda x: {"orders": [y[1] for y in x]})
