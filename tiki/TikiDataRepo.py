from typing import Optional, Callable
import os

from requests import Session
from authlib.integrations.requests_client import OAuth2Session

from returns.result import ResultE, Success, safe
from google.cloud import firestore

from tiki.Tiki import Event, Order, EventRes
from db.firestore import DB

BASE_URL = "https://api.tiki.vn/integration"
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)
TIKI_ACK_ID = DB.collection(
    "TikiAcks" if os.getenv("PYTHON_ENV") == "prod" else "TikiAcks-dev"
).document("tiki-ack-id")
TIKI_ORDERS = DB.collection(
    "TikiOrders" if os.getenv("PYTHON_ENV") == "prod" else "TikiOrders-dev"
)



def get_events(session: OAuth2Session) -> Callable[[Optional[str]], ResultE[EventRes]]:
    @safe
    def _get(ack_id: Optional[str] = None) -> EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull", json={"ack_id": ack_id}
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get

def get_ack_id() -> ResultE[Optional[str]]:
    return (
        safe(TIKI_ACK_ID.get)()
        .bind(lambda x: Success(x.to_dict()))
        .bind(safe(lambda x: x["ack_id"]))
        .lash(lambda _: Success(None))
    )


@safe
def update_ack_id(ack_id: str) -> str:
    TIKI_ACK_ID.update(
        {
            "ack_id": ack_id,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )
    return ack_id


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
                    "seller_income_detail": {
                        "item_qty": item["seller_income_detail"]["item_qty"],
                        "sub_total": item["seller_income_detail"]["sub_total"],
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

@safe
def persist_tiki_order(order: Order) -> Order:
    doc_ref = TIKI_ORDERS.document()
    doc_ref.create({
        "order": order,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    return order
