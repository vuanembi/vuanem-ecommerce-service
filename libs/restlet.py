from typing import Callable, TypedDict, Optional
import os
import json

from typing_extensions import Protocol
import oauthlib.oauth1
from requests_oauthlib import OAuth1Session


class Restlet(TypedDict):
    script: int
    deploy: int


class RestletRequest(Protocol):
    def __call__(
        self,
        session: OAuth1Session,
        params: dict = {},
        body: Optional[dict] = None,
    ) -> Optional[dict]:
        pass


BASE_URL = f"https://{os.getenv('ACCOUNT_ID')}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"


def oauth_session():
    return OAuth1Session(
        client_key=os.getenv("CONSUMER_KEY"),
        client_secret=os.getenv("CONSUMER_SECRET"),
        resource_owner_key=os.getenv("ACCESS_TOKEN"),
        resource_owner_secret=os.getenv("TOKEN_SECRET"),
        realm=os.getenv("ACCOUNT_ID"),
        signature_method=oauthlib.oauth1.SIGNATURE_HMAC_SHA256,
    )


def restlet(restlet: Restlet) -> Callable[[str], RestletRequest]:
    def request_restlet(method: str) -> RestletRequest:
        def request(
            session: OAuth1Session,
            params: dict = {},
            body: Optional[dict] = None,
        ) -> Optional[dict]:
            with session.request(
                method,
                BASE_URL,
                params={
                    **restlet,
                    **params,
                },
                json=body,
                headers={"Content-type": "application/json"},
            ) as r:
                if r.status_code == 400:
                    return None
                else:
                    return r.json()

        return request

    return request_restlet


sales_order = restlet({"script": 997, "deploy": 1})
customer = restlet({"script": 1099, "deploy": 1})
inventory_item = restlet({"script": 1101, "deploy": 1})
