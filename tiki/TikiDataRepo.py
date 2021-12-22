from typing import Optional, Callable
import os

from requests import Session

from returns.result import ResultE, safe
from google.cloud import firestore

from tiki.Tiki import Event, Order, EventRes
from firestore.FirestoreRepo import FIRESTORE, get_latest, persist

BASE_URL = "https://api.tiki.vn/integration"
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)

collection = FIRESTORE.collection(
    "TikiAcks" if os.getenv("PYTHON_ENV") == "prod" else "TikiAcks-dev"
)


def get_seller_info(session):
    @safe
    def _get(headers: dict):
        with session.get(f"{BASE_URL}/v2/sellers/me", headers=headers) as r:
            r.raise_for_status()
            return headers

    return _get


def get_events(session: Session) -> Callable[[Optional[str]], ResultE[EventRes]]:
    @safe
    def _get(ack_id: Optional[str] = None) -> EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull", json={"ack_id": ack_id}
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get


def extract_order(event: Event) -> str:
    return event["payload"]["order_code"]


def get_order(session: Session) -> Callable[[str], ResultE[Order]]:
    @safe
    def _get(order_id: str) -> Order:
        with session.get(
            f"{BASE_URL}/v2/orders/{order_id}",
            params={"include": "items.fees"},
        ) as r:
            data = r.json()
        return {
            "id": data["id"],
            "code": data["code"],
            "items": [
                {
                    "product": {
                        "name": item["product"]["name"],
                        "seller_product_code": item["product"]["seller_product_code"],
                    },
                    "qty": item["qty"],
                    "invoice": {
                        "row_total": item["invoice"]["row_total"],
                    },
                }
                for item in data["items"]
            ],
            "shipping": {
                "address": {
                    "full_name": data["shipping"]["address"]["full_name"],
                    "street": data["shipping"]["address"]["street"],
                    "ward": data["shipping"]["address"]["ward"],
                    "district": data["shipping"]["address"]["district"],
                    "phone": data["shipping"]["address"]["phone"],
                },
            },
        }

    return _get


get_latest_ack_id = get_latest(collection, "created_at")
persist_ack_id: Callable[[str], ResultE[firestore.DocumentReference]] = persist(
    collection,
    lambda ack_id: (
        str(ack_id),
        {
            "created_at": firestore.SERVER_TIMESTAMP,
        },
    ),
)
