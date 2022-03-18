from typing import TypedDict, Protocol, Union

import requests


class RequestBuilder(Protocol):
    def __call__(
        self,
        uri: str,
        method: str,
        params: dict[str, Union[int, str]] = {},
        body: dict[str, Union[int, str]] = {},
    ) -> requests.PreparedRequest:
        pass


class AccessToken(TypedDict):
    access_token: str
    refresh_token: str


OrderSN = str


class Item(TypedDict):
    item_name: str
    item_sku: str
    model_quantity_purchased: int
    model_original_price: int
    model_discounted_price: int


class Order(TypedDict):
    order_sn: OrderSN
    create_time: int
    update_time: int
    item_list: list[Item]


ItemsSchema = [
    {"name": "item_id", "type": "NUMERIC"},
    {"name": "category_id", "type": "NUMERIC"},
    {"name": "item_name", "type": "STRING"},
    {"name": "item_sku", "type": "STRING"},
    {"name": "create_time", "type": "NUMERIC"},
    {"name": "update_time", "type": "NUMERIC"},
    {
        "name": "attribute_list",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "attribute_id", "type": "NUMERIC"},
            {"name": "original_attribute_name", "type": "STRING"},
            {"name": "is_mandatory", "type": "BOOLEAN"},
            {
                "name": "attribute_value_list",
                "type": "record",
                "mode": "repeated",
                "fields": [
                    {"name": "value_id", "type": "NUMERIC"},
                    {"name": "original_value_name", "type": "STRING"},
                    {"name": "value_unit", "type": "STRING"},
                ],
            },
        ],
    },
    {
        "name": "price_info",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "currency", "type": "STRING"},
            {"name": "original_price", "type": "NUMERIC"},
            {"name": "current_price", "type": "NUMERIC"},
        ],
    },
    {
        "name": "stock_info",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "stock_type", "type": "NUMERIC"},
            {"name": "current_stock", "type": "NUMERIC"},
            {"name": "normal_stock", "type": "NUMERIC"},
            {"name": "reserved_stock", "type": "NUMERIC"},
        ],
    },
    {"name": "weight", "type": "STRING"},
    {
        "name": "dimension",
        "type": "record",
        "fields": [
            {"name": "package_length", "type": "NUMERIC"},
            {"name": "package_width", "type": "NUMERIC"},
            {"name": "package_height", "type": "NUMERIC"},
        ],
    },
    {
        "name": "logistic_info",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "logistic_id", "type": "NUMERIC"},
            {"name": "logistic_name", "type": "STRING"},
            {"name": "enabled", "type": "BOOLEAN"},
            {"name": "shipping_fee", "type": "NUMERIC"},
            {"name": "is_free", "type": "BOOLEAN"},
        ],
    },
    {
        "name": "pre_order",
        "type": "record",
        "fields": [
            {"name": "is_pre_order", "type": "BOOLEAN"},
            {"name": "days_to_ship", "type": "NUMERIC"},
        ],
    },
    {"name": "condition", "type": "STRING"},
    {"name": "size_chart", "type": "STRING"},
    {"name": "item_status", "type": "STRING"},
    {"name": "has_model", "type": "BOOLEAN"},
    {"name": "promotion_id", "type": "NUMERIC"},
    {
        "name": "brand",
        "type": "record",
        "fields": [
            {"name": "brand_id", "type": "NUMERIC"},
            {"name": "original_brand_name", "type": "STRING"},
        ],
    },
]
