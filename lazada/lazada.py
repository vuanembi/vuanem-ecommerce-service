from typing import Any, Callable, TypedDict

import requests

AuthBuilder = Callable[[str, dict[str, Any]], requests.PreparedRequest]


class AccessToken(TypedDict):
    access_token: str
    refresh_token: str
    refresh_expires_in: int
    expires_in: int
    expires_at: int


class Order(TypedDict):
    order_id: int
    created_at: str
    updated_at: str


class Item(TypedDict):
    sku: str
    name: str
    paid_price: float
    voucher_platform: float


class OrderItems(Order):
    items: list[Item]
