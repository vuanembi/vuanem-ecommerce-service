from typing import TypedDict, Optional

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

EventRes = tuple[str, Optional[list[Event]]]


# ----------------------------------- Order ---------------------------------- #


class Product(TypedDict):
    name: str
    seller_product_code: str


class Invoice(TypedDict):
    row_total: int


class Item(TypedDict):
    product: Product
    qty: int
    invoice: Invoice


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
