from typing import Callable, Optional
import os

import oauthlib.oauth1
from requests_oauthlib import OAuth1Session
from returns.result import ResultE, safe

from netsuite import Restlet


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


@safe
def request(
    session: OAuth1Session,
    restlet: Restlet.Restlet,
    method: str,
    params: dict = {},
    body: Optional[dict] = None,
) -> ResultE[dict]:
    with session.request(
        method,
        BASE_URL,
        params={**restlet, **params},
        json=body,
        headers={"Content-type": "application/json"},
    ) as r:
        r.raise_for_status()
        return r.json()
