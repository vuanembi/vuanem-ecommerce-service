from typing import Optional
import os

from authlib.integrations.requests_client import OAuth2Session
from returns.result import safe
from returns.functions import raise_exception

from tiki.tiki_repo import TIKI

TIKI_CLIENT_ID = "9636507817321643"

USER_AGENT = {
    "User-Agent": "PostmanRuntime/7.28.4",
}


@safe
def get_access_token() -> dict:
    return TIKI.get(["state.access_token"]).get("state.access_token")


def update_access_token(token: dict) -> None:
    TIKI.set({"state": {"access_token": token}}, merge=True)


def get_auth_session(token: Optional[dict]) -> OAuth2Session:
    session = OAuth2Session(
        TIKI_CLIENT_ID,
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
