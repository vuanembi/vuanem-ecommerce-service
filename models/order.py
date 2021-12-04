from typing import TypedDict
from datetime import date

from models.customer import Customer
from models.ecommerce import LEAD_SOURCE, Ecommerce


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
    memo: str


def build(
    customer: Customer, items: list[Item], ecommerce: Ecommerce, memo: str
) -> Order:
    return (
        {
            "leadsource": LEAD_SOURCE,
            "custbody_expecteddeliverytime": 4,
            "trandate": date.today().isoformat(),
        }
        | customer
        | ecommerce
        | {
            "item": items,
        }
        | {
            "memo": memo,
        }
    )
