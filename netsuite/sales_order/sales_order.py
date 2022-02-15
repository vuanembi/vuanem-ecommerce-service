from typing import TypedDict

from netsuite.customer import customer
from netsuite.item import item


EXPECTED_DELIVERY_TIME = 4
CUSTBODY_EXPECTED_SHIPPING_METHOD = 4
CUSTBODY_PRINT_FORM = True


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

SHOPEE_ECOMMERCE: Ecommerce = {
    "subsidiary": 1,
    "department": 1041,
    "location": 787,
    "custbody_order_payment_method": 41,
    "salesrep": 1664,
    "partner": 915574,
    "custbody_onl_rep": 933725,
}


class Detail(TypedDict):
    leadsource: int
    custbody_expecteddeliverytime: int
    custbody_expected_shipping_method: int
    trandate: str
    shipdate: str
    custbody_print_form: bool
    memo: str


class Order(customer.Customer, Detail, item.Items, Ecommerce):
    pass
