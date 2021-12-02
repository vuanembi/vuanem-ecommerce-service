from typing import TypedDict, Optional
import os

import requests

BASE_URL = "https://api.tiki.vn/integration"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('TIKI_ACCESS_TOKEN')}",
    "User-Agent": "PostmanRuntime/7.28.3",
}
QUEUE_CODE = "6cd68367-3bde-4aac-a24e-258bc907d68b"


class Payload(TypedDict):
    order_code: str
    status: str


class Event(TypedDict):
    id: str
    sid: str
    created_at: str
    payload: Payload


class Product(TypedDict):
    seller_product_code: str


class Item(TypedDict):
    product: Product
    qty: int
    price: int


class Address(TypedDict):
    full_name: str
    street: str
    ward: str
    district: str
    phone: str


class Shipping(TypedDict):
    address: Address


class Order(TypedDict):
    id: int
    code: str
    items: list[Item]
    shipping: Shipping


def pull_events(
    session: requests.Session,
    ack_id: Optional[str] = None,
) -> tuple[str, list[Event]]:
    with session.post(
        f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull",
        json={
            "ack_id": ack_id,
        },
        headers=HEADERS,
    ) as r:
        data = r.json()
    return data["ack_id"], data["events"]


def get_order(session: requests.Session, order_id: str) -> Order:
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
                    "seller_product_code": item["product"]["seller_product_code"],
                },
                "qty": item["qty"],
                "price": item["price"],
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
