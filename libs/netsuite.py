from typing import TypedDict, Optional
from datetime import date

from requests_oauthlib import OAuth1Session

from libs import restlet

LEAD_SOURCE = 144506
EXPECTED_DELIVERY_TIME = 4


class ShippingAddress(TypedDict):
    addressee: str


class CustomerBase(TypedDict):
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress


class Customer(CustomerBase):
    entity: int


class PreparedCustomer(CustomerBase):
    entity: None


class CustomerRequest(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str


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


class Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int


class OrderBase(TypedDict):
    leadsource: int
    custbody_expecteddeliverytime: int
    trandate: str
    item: list[Item]
    memo: str


class PreparedOrder(OrderBase, PreparedCustomer, Ecommerce):
    pass


class Order(OrderBase, Customer, Ecommerce):
    pass


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> Optional[str]:
    try:
        return restlet.inventory_item("GET")(session, params={"itemid": sku})["id"]
    except:
        return None


def get_customer_if_not_exist(
    session: OAuth1Session,
    customer: CustomerRequest,
) -> str:
    _customer = restlet.customer("GET")(session, params={"phone": customer["phone"]})
    return (
        _customer["id"]
        if _customer
        else restlet.customer("POST")(
            session,
            body={
                "leadsource": LEAD_SOURCE,
                "firstname": customer["firstname"],
                "lastname": customer["lastname"],
                "phone": customer["phone"],
            },
        )["id"]
    )


def create_sales_order(session: OAuth1Session, order: Order) -> str:
    return restlet.sales_order("POST")(session, body=order)["id"]


def build_customer_request(name: str, phone: str) -> CustomerRequest:
    return {
        "leadsource": LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def build_prepared_customer(phone: str, name: str) -> PreparedCustomer:
    return {
        "entity": None,
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }


def build_prepared_order(
    customer: PreparedCustomer,
    items: list[Item],
    ecommerce: Ecommerce,
    memo: str,
) -> PreparedOrder:
    order = {
        "leadsource": LEAD_SOURCE,
        "custbody_expecteddeliverytime": EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "item": items,
        "memo": memo,
    }
    # return {
    #     "leadsource": LEAD_SOURCE,
    #     "custbody_expecteddeliverytime": EXPECTED_DELIVERY_TIME,
    #     "trandate": date.today().isoformat(),
    #     "item": items,
    #     "memo": memo,
    #     **customer, # type: ignore
    #     **ecommerce,
    # }
    return order | customer | ecommerce
