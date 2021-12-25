import os

from authlib.integrations.requests_client import OAuth2Session
from returns.result import safe
from returns.functions import raise_exception

from auth.AccessTokenRepo import ACCESS_TOKEN

USER_AGENT = {
    "User-Agent": "PostmanRuntime/7.28.4",
}
TIKI_ACCESS_TOKEN = ACCESS_TOKEN.document("tiki")


@safe
def get_access_token() -> dict:
    return TIKI_ACCESS_TOKEN.get().to_dict()


@safe
def update_access_token(token: dict) -> None:
    TIKI_ACCESS_TOKEN.update(token)


def get_auth_session(token: dict) -> OAuth2Session:
    session = OAuth2Session(
        os.getenv("TIKI_CLIENT_ID"),
        os.getenv("TIKI_CLIENT_SECRET"),
        token=token,
        token_endpoint_auth_method="client_secret_basic",
        token_endpoint="https://api.tiki.vn/sc/oauth2/token",
        grant_type="client_credentials",
    )
    if session.token.is_expired():
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
