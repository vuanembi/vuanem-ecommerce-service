from returns.result import safe
import requests

from shopee import shopee, shopee_repo

auth_request = shopee_repo.build_shopee_request()


@safe
def get_token(session: requests.Session, code: str):
    with session.send(
        auth_request(
            "auth/token/get",
            {
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
def refresh_token(session: requests.Session, access_token: shopee.AccessToken):
    with session.send(
        auth_request(
            "auth/access_token/get",
            {
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
def get_access_token() -> shopee.AccessToken:
    return shopee_repo.SHOPEE.get(["state.access_token"]).get("state.access_token")


@safe
def update_access_token(token: shopee.AccessToken) -> shopee.AccessToken:
    shopee_repo.SHOPEE.set({"state": {"access_token": token}}, merge=True)
    return token
