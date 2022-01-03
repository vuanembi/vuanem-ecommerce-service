import requests
from returns.result import ResultE, Success, safe
from returns.functions import raise_exception
from returns.iterables import Fold
from returns.pipeline import flow
from returns.pointfree import bind

from common import utils
from lazada import lazada, auth_repo, data_repo


def _update_new_token(session: requests.Session):
    def _update(token: lazada.AccessToken) -> ResultE[lazada.AccessToken]:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )

    return _update


def auth_service(session: requests.Session) -> ResultE[lazada.AuthBuilder]:
    return (
        auth_repo.get_access_token()
        .bind(utils.check_expired)  # type: ignore
        .lash(_update_new_token(session))
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


def get_order_details(
    session: requests.Session,
    auth_builder: lazada.AuthBuilder,
    created_after: str = "2022-01-01T00:00:00",
):
    return flow(
        created_after,
        data_repo.get_orders(session, auth_builder),
        bind(_get_items(session, auth_builder)),
        bind(
            lambda orders: Fold.collect_all(  # type: ignore
                [data_repo.persist_order(order) for order in orders], # type: ignore
                Success(()),
            )
        ),
        bind(data_repo.persist_max_created_at),
    )
