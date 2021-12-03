from typing import TypedDict

LEAD_SOURCE = 144506

class Ecommerce(TypedDict):
    custbody_order_payment_method: int
    salesrep: int
    partner: int
    location: int
    custbody_onl_rep: int

Tiki: Ecommerce = {
    "custbody_order_payment_method": 23,
    "salesrep": 1664,
    "partner": 916906,
    "location": 788,
    "custbody_onl_rep": 942960,
}
