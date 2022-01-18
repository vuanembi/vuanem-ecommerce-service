from typing import Any, Callable, TypedDict

import requests

AuthBuilder = Callable[[str, dict[str, Any]], requests.PreparedRequest]


class AccessToken(TypedDict):
    access_token: str
    refresh_token: str

class AuthParams(TypedDict):
    shop_id: int
    access_token: str


class OrderStatusPushData(TypedDict):
    ordersn: str
    status: str


class OrderStatusPush(TypedDict):
    shop_id: int
    code: int
    timestamp: int
    data: OrderStatusPushData


class Item(TypedDict):
    variation_sku: str
    variation_quantity_purchased: int
    variation_original_price: int
    variation_discounted_price: int


class Order(TypedDict):
    ordersn: str
    items: list[Item]
