from typing import Optional
import os

import oauthlib.oauth1
from requests_oauthlib import OAuth1Session

from restlet.Restlet import Restlet, RestletRequest


BASE_URL = f"https://{os.getenv('ACCOUNT_ID')}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"


def netsuite_session() -> OAuth1Session:
    return OAuth1Session(
        client_key=os.getenv("CONSUMER_KEY"),
        client_secret=os.getenv("CONSUMER_SECRET"),
        resource_owner_key=os.getenv("ACCESS_TOKEN"),
        resource_owner_secret=os.getenv("TOKEN_SECRET"),
        realm=os.getenv("ACCOUNT_ID"),
        signature_method=oauthlib.oauth1.SIGNATURE_HMAC_SHA256,
    )


def request_restlet(restlet: Restlet) -> RestletRequest:
    def request(
        session: OAuth1Session,
        method: str,
        params: dict = {},
        body: Optional[dict] = None,
    ) -> dict:
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
            r.raise_for_status()
            return r.json()

    return request


sales_order = request_restlet({"script": 997, "deploy": 1})
customer = request_restlet({"script": 1099, "deploy": 1})
inventory_item = request_restlet({"script": 1101, "deploy": 1})
