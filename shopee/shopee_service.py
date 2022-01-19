from datetime import datetime

import requests
from returns.result import ResultE, Success
from returns.functions import raise_exception
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.curry import curry
from returns.converters import flatten

from common import utils
from shopee import shopee, shopee_repo, auth_repo, data_repo
from netsuite import netsuite, netsuite_service, prepare_repo


def _token_refresh_service(token: shopee.AccessToken) -> ResultE[shopee.AccessToken]:
    with requests.Session() as session:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )


def auth_service() -> ResultE[shopee.RequestBuilder]:
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
            data_repo.get_orders(session, request_builder),
            bind(data_repo.get_order_items(session, request_builder)),
            map_(lambda x: [i for i in x if i['create_time'] != create_time]), # type: ignore
            bind(data_repo.persist_max_created_at),
        )


def get_orders_service() -> ResultE[list[shopee.Order]]:
    return flatten(
        flow(  # type: ignore
            Success(_get_orders_items),
            auth_service().apply,
            data_repo.get_max_created_at().apply,
        )
    )
