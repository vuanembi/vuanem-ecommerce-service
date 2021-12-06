from typing import TypedDict
from datetime import date

from models.netsuite.customer import CustomerBase, Customer, PreparedCustomer
from models.netsuite.ecommerce import LEAD_SOURCE, Ecommerce

EXPECTED_DELIVERY_TIME = 4


class Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int


class OrderBase(CustomerBase, Ecommerce):
    leadsource: int
    custbody_expecteddeliverytime: int
    trandate: str
    item: list[Item]
    memo: str

class PreparedOrder(PreparedCustomer, Ecommerce):
    pass

class Order(Customer, Ecommerce):
    pass


def build_item(item: str, quantity: int, amount: int) -> Item:
    return {
        "item": int(item),
        "quantity": quantity,
        "price": -1,
        "amount": int(amount / 1.1),
    }


def build_prepared_order(
    customer: PreparedCustomer,
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
