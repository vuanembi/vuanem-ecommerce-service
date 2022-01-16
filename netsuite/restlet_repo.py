from typing import Optional
import os

from oauthlib.oauth1 import SIGNATURE_HMAC_SHA256
from requests_oauthlib import OAuth1Session
from returns.result import safe

from netsuite import restlet


BASE_URL = f"https://{os.getenv('ACCOUNT_ID')}.restlets.api.netsuite.com/app/site/hosting/restlet.nl"


class RestletError(Exception):
    pass


def netsuite_session() -> OAuth1Session:
    return OAuth1Session(
        client_key=os.getenv("CONSUMER_KEY"),
        client_secret=os.getenv("CONSUMER_SECRET"),
        resource_owner_key=os.getenv("ACCESS_TOKEN"),
        resource_owner_secret=os.getenv("TOKEN_SECRET"),
        realm=os.getenv("ACCOUNT_ID"),
        signature_method=SIGNATURE_HMAC_SHA256,
    )


@safe
def request(
    session: OAuth1Session,
    restlet: restlet.Restlet,
    method: str,
    params: dict = {},
    body: Optional[dict] = None,
) -> dict[str, str]:
    with session.request(
        method,
        BASE_URL,
        params={**restlet, **params},
        json=body,
        headers={
            "Content-Type": "application/json",
        },
    ) as r:
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 400:
            raise RestletError(r.json())
        else:
            r.raise_for_status()
            return {}
