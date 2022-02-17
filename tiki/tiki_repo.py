from typing import Optional, Callable

import os

from requests import Session
from returns.result import ResultE, safe
from authlib.integrations.requests_client import OAuth2Session
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
            "fulfillment_type": data.get("fulfillment_type"),
            "status": data.get("status"),
            "inventory_status": data.get("inventory_status"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    return _get
