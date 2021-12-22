import os

from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from google.cloud import firestore

from returns.result import safe

from firestore.FirestoreRepo import FIRESTORE, get_latest, persist

collection = FIRESTORE.collection(
    "TikiAccessToken" if os.getenv("PYTHON_ENV") == "prod" else "TikiAccessToken-dev"
)

USER_AGENT = {
    "User-Agent": "PostmanRuntime/7.28.4",
}


@safe
def get_new_access_token(*args) -> str:
    token = OAuth2Session(
        client=BackendApplicationClient(client_id=os.getenv("TIKI_CLIENT_ID"))
    ).fetch_token(
        token_url="https://api.tiki.vn/sc/oauth2/token",
        auth=HTTPBasicAuth(
            os.getenv("TIKI_CLIENT_ID"), os.getenv("TIKI_CLIENT_SECRET")
        ),
        headers={**USER_AGENT},
    )
    return token["access_token"]


get_latest_access_token = get_latest(collection, "created_at")
persist_access_token = persist(
    collection,
    lambda access_token: (
        None,
        {
            "access_token": access_token,
            "created_at": firestore.SERVER_TIMESTAMP,
        },
    ),
)


def build_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        **USER_AGENT,
    }
