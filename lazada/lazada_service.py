from typing import Any
from datetime import datetime

import requests
from returns.result import Result, ResultE, Success, safe
from returns.functions import raise_exception
from returns.iterables import Fold
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.curry import curry
from returns.converters import flatten

from common import utils
from lazada import lazada, auth_repo, data_repo


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
            bind(
                lambda orders: Fold.collect_all(  # type: ignore
                    [data_repo.persist_order(order) for order in orders],  # type: ignore
                    Success(()),
                )
            ),
            map_(list)
            # bind(data_repo.persist_max_created_at),
        )


def get_order_service() -> ResultE[list[lazada.OrderItems]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders),
            auth_service().apply,
            data_repo.get_max_created_at().apply,
        )
    )
