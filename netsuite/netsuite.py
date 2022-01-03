from typing import TypedDict

# ---------------------------------- Default --------------------------------- #

LEAD_SOURCE = 144506
EXPECTED_DELIVERY_TIME = 4
CUSTBODY_EXPECTED_SHIPPING_METHOD = 4
CUSTBODY_PRINT_FORM = True
CUSTCOL_DELIVER_LOCATION = 50
COMMIT_INVENTORY = 3

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


class CustomerReq(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str


TIKI_CUSTOMER: Customer = {
    "entity": 979199,
    "custbody_customer_phone": "1998103102",
    "custbody_recipient_phone": "1998103102",
    "custbody_recipient": "TEMP Tiki",
    "shippingaddress": {
        "addressee": "TEMP Tiki",
    },
}

LAZADA_CUSTOMER: Customer = {
    "entity": 985867,
    "custbody_customer_phone": "1998103103",
    "custbody_recipient_phone": "1998103103",
    "custbody_recipient": "TEMP Lazada",
    "shippingaddress": {
        "addressee": "TEMP Lazada",
    },
}

SHOPEE_CUSTOMER: Customer = {
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


TIKI_ECOMMERCE: Ecommerce = {
    "subsidiary": 1,
    "department": 1044,
    "location": 788,
    "custbody_order_payment_method": 23,
    "salesrep": 1664,
    "partner": 916906,
    "custbody_onl_rep": 942960,
}

LAZADA_ECOMMERCE: Ecommerce = {
    "subsidiary": 1,
    "department": 1044,
    "location": 789,
    "custbody_order_payment_method": 44,
    "salesrep": 1664,
    "partner": 923414,
    "custbody_onl_rep": 722312,
}

SHOPEE_COMMERCE: Ecommerce = {
    "subsidiary": 1,
    "department": 1041,
    "location": 787,
    "custbody_order_payment_method": 41,
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
    commitinventory: int
    location: int
    custcol_deliver_location: int


class Items(TypedDict):
    item: list[Item]


class OrderMeta(TypedDict):
    leadsource: int
    custbody_expecteddeliverytime: int
    custbody_expected_shipping_method: int
    trandate: str
    shipdate: str
    custbody_print_form: bool
    memo: str


class PreparedOrder(PreparedCustomer, OrderMeta, Items, Ecommerce):
    pass


class Order(Customer, OrderMeta, Items, Ecommerce):
    pass
