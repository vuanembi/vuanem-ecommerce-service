from typing import TypedDict

# ----------------------------------- Auth ----------------------------------- #


class Auth(TypedDict):
    access_token: str
    expires_in: int


# ----------------------------------- Event ---------------------------------- #


class Payload(TypedDict):
    order_code: str
    status: str


class Event(TypedDict):
    id: str
    sid: str
    created_at: str
    payload: Payload


EventRes = tuple[str, list[Event]]


# ----------------------------------- Order ---------------------------------- #


class Product(TypedDict):
    name: str
    seller_product_code: str


class DiscountCoupon(TypedDict):
    seller_discount: int


class Discount(TypedDict):
    discount_coupon: DiscountCoupon


class SellerIncomeDetail(TypedDict):
    item_price: int
    item_qty: int
    sub_total: int
    discount: Discount


class Item(TypedDict):
    _fulfillment_type: str
    product: Product
    seller_income_detail: SellerIncomeDetail


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
    fulfillment_type: str
    status: str
    inventory_status: str
    items: list[Item]
    shipping: Shipping
    created_at: str
    updated_at: str


ProductsSchema = [
    {"name": "product_id", "type": "NUMERIC"},
    {"name": "sku", "type": "STRING"},
    {"name": "name", "type": "STRING"},
    {"name": "master_id", "type": "NUMERIC"},
    {"name": "master_sku", "type": "STRING"},
    {"name": "super_id", "type": "NUMERIC"},
    {"name": "super_sku", "type": "STRING"},
    {"name": "active", "type": "NUMERIC"},
    {"name": "original_sku", "type": "STRING"},
    {"name": "type", "type": "STRING"},
    {"name": "entity_type", "type": "STRING"},
    {"name": "price", "type": "NUMERIC"},
    {"name": "market_price", "type": "NUMERIC"},
    {"name": "created_at", "type": "TIMESTAMP"},
    {"name": "updated_at", "type": "TIMESTAMP"},
    {"name": "thumbnail", "type": "STRING"},
    {
        "name": "categories",
        "type": "record",
        "mode": "repeated",
        "fields": [
            {"name": "id", "type": "NUMERIC"},
            {"name": "name", "type": "STRING"},
            {"name": "url_key", "type": "STRING"},
            {"name": "is_primary", "type": "BOOLEAN"},
        ],
    },
]
