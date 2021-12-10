from typing import TypedDict

from models.netsuite import ecommerce, customer


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


class PreparedOrder(customer.PreparedCustomer, OrderMeta, Items, ecommerce.Ecommerce):  # type: ignore
    pass


class Order(customer.Customer, OrderMeta, Items, ecommerce.Ecommerce):  # type: ignore
    pass
