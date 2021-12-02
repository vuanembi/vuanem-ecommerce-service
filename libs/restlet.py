from typing import Callable, TypedDict, Optional
import os
import json
from urllib.parse import urlencode

from typing_extensions import Protocol
import requests
import oauthlib.oauth1


class Restlet(TypedDict):
    script: int
    deploy: int


class RestletRequest(Protocol):
    def __call__(
        self,
        session: requests.Session,
        params: Optional[dict] = None,
        body: Optional[dict] = None,
    ) -> dict:
        pass

OAUTH_CLIENT = oauthlib.oauth1.Client(
    client_key=os.getenv("CONSUMER_KEY"),
    client_secret=os.getenv("CONSUMER_SECRET"),
    resource_owner_key=os.getenv("ACCESS_TOKEN"),
    resource_owner_secret=os.getenv("TOKEN_SECRET"),
    realm=os.getenv("ACCOUNT_ID"),
    signature_method=oauthlib.oauth1.SIGNATURE_HMAC_SHA256,
)

BASE_URL = f"https://{os.getenv('ACCOUNT_ID')}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"


def restlet(restlet: Restlet) -> Callable[[str], RestletRequest]:
    def request_restlet(method: str) -> RestletRequest:
        def request(
            session: requests.Session,
            params: Optional[dict] = None,
            body: Optional[dict] = None,
        ) -> dict:
            url, headers, body = OAUTH_CLIENT.sign(
                uri=f"{BASE_URL}?{urlencode({**restlet, **params}) if params else urlencode({**restlet})}",
                http_method=method,
                body=body,
                headers={
                    "Content-type": "application/json",
                },
            )
            with session.request(method, url, headers=headers) as r:
                return json.loads(r.json())

        return request

    return request_restlet


sales_order = restlet({"script": 997, "deploy": 1})
customer = restlet({"script": 1099, "deploy": 1})
inventory_item = restlet({"script": 1101, "deploy": 1})
