from typing import Optional, Callable

import os

from requests import Session
from returns.result import ResultE, safe
from authlib.integrations.requests_client import OAuth2Session
from google.cloud import firestore

from db.firestore import DB
from tiki import tiki


BASE_URL = "https://api.tiki.vn/integration"
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)
TIKI = DB.document("Tiki")


def get_events(session: OAuth2Session):
    @safe
    def _get(ack_id: Optional[str] = None) -> tiki.EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull",
            json={
                "ack_id": ack_id,
            },
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get


# @safe
# def get_ack_id() -> str:
#     return TIKI.get(["state.ack.ack_id"]).get("state.ack.ack_id")


# @safe
# def update_ack_id(ack_id: str) -> str:
#     TIKI.set(
#         {
#             "state": {
#                 "ack": {
#                     "ack_id": ack_id,
#                     "updated_at": firestore.SERVER_TIMESTAMP,
#                 }
#             }
#         },
#         merge=True,
#     )
#     return ack_id


def extract_order(event: tiki.Event) -> str:
    return event["payload"]["order_code"]


def get_order(session: Session) -> Callable[[str], ResultE[tiki.Order]]:
    @safe
    def _get(order_id: str) -> tiki.Order:
        with session.get(
            f"{BASE_URL}/v2/orders/{order_id}",
            params={
                "include": "items.fees",
            },
        ) as r:
            data = r.json()
        return data

    return _get
