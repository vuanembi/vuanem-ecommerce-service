from typing import TypedDict
from datetime import date

from models.customer import Customer
from models.ecommerce import LEAD_SOURCE, Ecommerce

EXPECTED_DELIVERY_TIME = 4


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


def build_item(item: str, quantity: int, amount: int) -> Item:
    return {
        "item": int(item),
        "quantity": quantity,
        "price": -1,
        "amount": int(amount / 1.1),
    }


def build(
    customer: Customer,
    items: list[Item],
    ecommerce: Ecommerce,
    memo: str,
) -> Order:
    return (
        {
            "leadsource": LEAD_SOURCE,
            "custbody_expecteddeliverytime": EXPECTED_DELIVERY_TIME,
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
