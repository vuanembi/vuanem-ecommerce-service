from typing import TypedDict, Optional
import os

import requests

BASE_URL = "https://api.tiki.vn/integration"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
    "User-Agent": "PostmanRuntime/7.28.3",
}


class Payload(TypedDict):
    order_code: str
    status: str


class Event(TypedDict):
    id: str
    sid: str
    created_at: str
    payload: Payload


class EventRes(TypedDict):
    ack_id: str
    events: list[Event]


class Product(TypedDict):
    seller_product_code: str


class Item(TypedDict):
    product: Product
    qty: int


class Address(TypedDict):
    full_name: str
    street: str
    ward: str
    district: str
    region: str
    country: str
    phone: str


class Shipping(TypedDict):
    address: str


class Order(TypedDict):
    id: int
    code: str
    items: list[Item]
    shipping: Shipping


def pull_events(session: requests.Session, ack_id: Optional[str] = None) -> EventRes:
    with session.post(
        f"{BASE_URL}/v1/queues/{os.getenv('QUEUE_CODE')}/events/pull",
        json={
            "ack_id": ack_id,
        },
        headers=HEADERS,
    ) as r:
        return r.json()


def get_order(session: requests.Session, order_id: str) -> Order:
    with session.get(
        f"{BASE_URL}/v2/orders/{order_id}",
        params={
            "include": "items.fees",
        },
        headers=HEADERS,
    ) as r:
        return r.json()


with requests.Session() as session:
    # x = pull_events(session, "fbf93903-8cf4-4ae8-8c1e-24cb73e016f7")
    x = get_order(session, "753075217")
    x
