from typing import Callable
import time

import requests
from returns.result import ResultE, safe

from db.firestore import DB
from lazada import lazada, lazada_repo

LAZADA = DB.document("Lazada")

auth_request = lazada_repo.build_lazada_request("https://api.lazada.com/rest")


@safe
def get_access_token() -> lazada.AccessToken:
    return LAZADA.get(["state.access_token"]).get("state.access_token")


@safe
def update_access_token(token: lazada.AccessToken) -> lazada.AccessToken:
    LAZADA.set({"state": {"access_token": token}}, merge=True)
    return token


@safe
def refresh_token(
    session: requests.Session,
    token: lazada.AccessToken,
) -> lazada.AccessToken:
    with session.send(
        auth_request(
            "/auth/token/refresh",
            {"refresh_token": token["refresh_token"]},
        )
    ) as r:
        res = r.json()
    return {
        **res,  # type: ignore
        "expires_at": int(time.time()) + int(res["expires_in"]),
    }
