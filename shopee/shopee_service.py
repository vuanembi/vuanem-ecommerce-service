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
from shopee import shopee, shopee_repo, auth_repo
from netsuite import netsuite, netsuite_service, prepare_repo


def _token_refresh_service(token: shopee.AccessToken) -> ResultE[shopee.AccessToken]:
    with requests.Session() as session:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )


def auth_service() -> ResultE[shopee.AuthBuilder]:
    return (
        auth_repo.get_access_token()
        .bind(_token_refresh_service)
        .map(lambda x: x["access_token"])
        .map(lambda x : shopee_repo.build_shopee_request(x, "query"))
    )
