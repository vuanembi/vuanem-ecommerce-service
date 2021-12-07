from typing import Optional
import os

import requests

from models.ecommerce import tiki

BASE_URL = "https://api.tiki.vn/integration"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('TIKI_ACCESS_TOKEN')}",
    "User-Agent": "PostmanRuntime/7.28.3",
}
QUEUE_CODE = "6cd68367-3bde-4aac-a24e-258bc907d68b"


def pull_events(
    session: requests.Session,
    ack_id: Optional[str] = None,
) -> tuple[str, list[tiki.Event]]:
    with session.post(
        f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull",
        json={
            "ack_id": ack_id,
        },
        headers=HEADERS,
    ) as r:
        data = r.json()
    return data["ack_id"], data["events"]


def get_order(session: requests.Session, order_id: str) -> tiki.Order:
    with session.get(
        f"{BASE_URL}/v2/orders/{order_id}",
        params={
            "include": "items.fees",
        },
        headers=HEADERS,
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
