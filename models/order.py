from typing import TypedDict
from datetime import date

from models.customer import Customer
from models.ecommerce import Ecommerce


class Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int


class Order(Customer, Ecommerce):
    leadsource: int
    custbody_expecteddeliverytime: int
    trandate: str
    item: list[Item]


def build(customer: Customer, items: list[Item], ecommerce: Ecommerce) -> Order:
    return {
        "leadsource": 144506,
        "custbody_expecteddeliverytime": 4,
        "trandate": date.today().isoformat(),
        **ecommerce,  # type: ignore
        **customer,
        "item": items,
    }
