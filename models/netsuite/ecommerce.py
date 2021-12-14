from typing import TypedDict


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
