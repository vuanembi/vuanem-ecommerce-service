from typing import TypedDict

# ---------------------------------- Default --------------------------------- #

LEAD_SOURCE = 144506
EXPECTED_DELIVERY_TIME = 4

# --------------------------------- Customer --------------------------------- #


class ShippingAddress(TypedDict):
    addressee: str


class PreparedCustomer(TypedDict):
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress


class Customer(PreparedCustomer):
    entity: int


class CustomerRequest(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str


ShopeeMock: Customer = {
    "entity": 966287,
    "custbody_customer_phone": "1998103101",
    "custbody_recipient_phone": "1998103101",
    "custbody_recipient": "TEMP Shopee",
    "shippingaddress": {
        "addressee": "TEMP Shopee",
    },
}

# --------------------------------- Ecommerce -------------------------------- #


class Ecommerce(TypedDict):
    subsidiary: int
    department: int
    custbody_order_payment_method: int
    salesrep: int
    partner: int
    location: int
    custbody_onl_rep: int


Tiki: Ecommerce = {
    "subsidiary": 1,
    "department": 1044,
    "location": 788,
    "custbody_order_payment_method": 23,
    "salesrep": 1664,
    "partner": 916906,
    "custbody_onl_rep": 942960,
}

Shopee: Ecommerce = {
    "subsidiary": 1,
    "department": 1041,
    "location": 787,
    "custbody_order_payment_method": 23,
    "salesrep": 1664,
    "partner": 915574,
    "custbody_onl_rep": 933725,
}

# ----------------------------------- Order ---------------------------------- #


class Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int


class Items(TypedDict):
    item: list[Item]


class OrderMeta(TypedDict):
    leadsource: int
    custbody_expecteddeliverytime: int
    trandate: str
    memo: str


class PreparedOrder(PreparedCustomer, OrderMeta, Items, Ecommerce):
    pass


class Order(Customer, OrderMeta, Items, Ecommerce):
    pass
