from typing import Optional
import os

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, safe
from returns.functions import raise_exception

from tiki.tiki_repo import TIKI

USER_AGENT = {
    "User-Agent": "PostmanRuntime/7.28.4",
}


def get_access_token() -> ResultE[Optional[dict]]:
    return safe(lambda x: x["state"]["access_token"])(TIKI.get().to_dict())


def update_access_token(token: dict) -> None:
    TIKI.set({"state": {"access_token": token}}, merge=True)


def get_auth_session(token: dict) -> OAuth2Session:
    session = OAuth2Session(
        os.getenv("TIKI_CLIENT_ID"),
        os.getenv("TIKI_CLIENT_SECRET"),
        token=token,
        token_endpoint_auth_method="client_secret_basic",
        token_endpoint="https://api.tiki.vn/sc/oauth2/token",
        grant_type="client_credentials",
    )
    if not token or session.token.is_expired():
        (
            safe(session.fetch_token)(
                headers={
                    **USER_AGENT,
                    "content-type": "application/x-www-form-urlencoded",
                }
            )
            .bind(safe(dict))
            .map(update_access_token)
            .lash(raise_exception)
        )
    session.headers.update(USER_AGENT)
    return session
