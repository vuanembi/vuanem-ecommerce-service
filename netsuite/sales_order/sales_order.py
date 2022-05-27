from typing import TypedDict, Optional

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


class _Detail(TypedDict):
    leadsource: int
    custbody_expecteddeliverytime: int
    custbody_expected_shipping_method: int
    trandate: str
    shipdate: str
    custbody_print_form: bool
    memo: str


class Detail(_Detail, total=False):
    id: Optional[int]


class Order(customer.Customer, Detail, item.Items, Ecommerce):
    pass
