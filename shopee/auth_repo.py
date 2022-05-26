from datetime import datetime

from returns.result import safe
import requests

from common.seller import Seller
from shopee import shopee, shopee_repo


def auth_request(seller: Seller):
    return shopee_repo.build_shopee_request(seller=seller, shop_id_position="body")


@safe
def get_token(seller: Seller, session: requests.Session, code: str):
    with session.send(
        auth_request(seller)(
            "auth/token/get",
            method="POST",
            body={
                "code": code,
            },
        )
    ) as r:
        r.raise_for_status()
        res = r.json()
    return {
        "access_token": res["access_token"],
        "refresh_token": res["refresh_token"],
    }


@safe
def refresh_token(
    seller: Seller,
    session: requests.Session,
    access_token: shopee.AccessToken,
):
    with session.send(
        auth_request(seller)(
            "auth/access_token/get",
            method="POST",
            body={
                "refresh_token": access_token["refresh_token"],
            },
        )
    ) as r:
        r.raise_for_status()
        res = r.json()
    return {
        "access_token": res["access_token"],
        "refresh_token": res["refresh_token"],
    }


@safe
def get_access_token(seller: Seller) -> shopee.AccessToken:
    return seller.db.get(["state.access_token"]).get("state.access_token")


def update_access_token(seller: Seller) -> shopee.AccessToken:
    @safe
    def _update(token: shopee.AccessToken) -> shopee.AccessToken:
        seller.db.set(
            {
                "state": {
                    "access_token": {
                        **token, # type: ignore
                        "updated_at": datetime.utcnow(),
                    }
                }
            },
            merge=True,
        )
        return token

    return _update
