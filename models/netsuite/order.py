from typing import TypedDict

from models.netsuite import customer, ecommerce

EXPECTED_DELIVERY_TIME = 4


class Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int


class OrderBase(customer.CustomerBase, ecommerce.Ecommerce):
    leadsource: ecommerce.LEAD_SOURCE
    custbody_expecteddeliverytime: int
    trandate: str
    item: list[Item]
    memo: str

class PreparedOrder(customer.PreparedCustomer, ecommerce.Ecommerce):
    pass

class Order(customer.Customer, ecommerce.Ecommerce):
    pass
