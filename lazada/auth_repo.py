import time

import requests
from returns.result import safe

from common.seller import Seller
from lazada import lazada, lazada_repo

auth_request = lazada_repo.build_lazada_request("https://api.lazada.com/rest")


@safe
def get_access_token(seller: Seller) -> lazada.AccessToken:
    return seller.db.get(["state.access_token"]).get("state.access_token")


def update_access_token(seller: Seller):
    @safe
    def _update(
        token: lazada.AccessToken,
    ) -> lazada.AccessToken:
        seller.db.set({"state": {"access_token": token}}, merge=True)
        return token

    return _update


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
