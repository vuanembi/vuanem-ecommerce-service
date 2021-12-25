import os

from authlib.integrations.requests_client import OAuth2Session
from returns.result import safe
from returns.functions import raise_exception

from db.firestore import DB

USER_AGENT = {
    "User-Agent": "PostmanRuntime/7.28.4",
}
_access_token = DB.document("Tiki").collection("AccessToken")
ACCESS_TOKEN_DOC = _access_token.document("access_token")

@safe
def get_access_token() -> dict:
    return ACCESS_TOKEN_DOC.get().to_dict()


def update_access_token(token: dict) -> None:
    ACCESS_TOKEN_DOC.update(token)


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
