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


ProductsSchema = [
    {"name": "item_id", "type": "NUMERIC"},
    {"name": "created_time", "type": "TIMESTAMP"},
    {"name": "updated_time", "type": "TIMESTAMP"},
    {
        "name": "skus",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "Status", "type": "STRING"},
            {"name": "quantity", "type": "NUMERIC"},
            {"name": "SellerSku", "type": "STRING"},
            {"name": "ShopSku", "type": "STRING"},
            {"name": "Url", "type": "STRING"},
            {
                "name": "multiWarehouseInventories",
                "type": "record",
                "mode": "repeated",
                "fields": [
                    {"name": "occupyQuantity", "type": "NUMERIC"},
                    {"name": "quantity", "type": "NUMERIC"},
                    {"name": "totalQuantity", "type": "NUMERIC"},
                    {"name": "withholdQuantity", "type": "NUMERIC"},
                    {"name": "warehouseCode", "type": "STRING"},
                    {"name": "sellableQuantity", "type": "NUMERIC"},
                ],
            },
            {"name": "package_width", "type": "STRING"},
            {"name": "package_height", "type": "STRING"},
            {"name": "special_price", "type": "NUMERIC"},
            {"name": "price", "type": "NUMERIC"},
            {
                "name": "channelInventories",
                "type": "record",
                "mode": "repeated",
                "fields": [
                    {"name": "channelName", "type": "STRING"},
                    {"name": "startTime", "type": "TIMESTAMP"},
                    {"name": "endTime", "type": "TIMESTAMP"},
                    {"name": "sellableQuantity", "type": "NUMERIC"},
                ],
            },
            {"name": "package_length", "type": "STRING"},
            {"name": "package_weight", "type": "STRING"},
            {"name": "SkuId", "type": "NUMERIC"},
        ],
    },
    {"name": "primary_category", "type": "NUMERIC"},
]
