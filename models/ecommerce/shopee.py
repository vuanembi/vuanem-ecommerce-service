from typing import TypedDict


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
