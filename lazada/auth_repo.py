from typing import Any
import os
from datetime import datetime
import hashlib
import hmac

import requests
from returns.result import safe

from db.firestore import DB
from lazada import lazada, lazada_repo

LAZADA = DB.document("Lazada")

auth_request = lazada_repo.build_lazada_request("https://api.lazada.com/rest")


@safe
def get_access_token() -> dict:
    return LAZADA.get(["state.access_token"]).get("state.access_token")


def update_access_token(token: lazada.AccessToken) -> None:
    LAZADA.set({"state": {"access_token": token}}, merge=True)


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
        return r.json()
