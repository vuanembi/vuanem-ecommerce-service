import os

from typing import Callable, Optional, TypeVar
from datetime import date

from requests_oauthlib import OAuth1Session

from libs import restlet
from models.netsuite import customer, order

LEAD_SOURCE = 144506
EXPECTED_DELIVERY_TIME = 4


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> Optional[str]:
    try:
        return restlet.inventory_item(session, "GET", params={"itemid": sku})["id"]
    except Exception as e:
        return None


def get_customer_if_not_exist(
    session: OAuth1Session,
    customer: customer.CustomerRequest,
) -> str:
    _customer = restlet.customer(session, "GET", params={"phone": customer["phone"]})
    return (
        _customer["id"]
        if _customer
        else restlet.customer(
            session,
            "POST",
            body={
                "leadsource": LEAD_SOURCE,
                "firstname": customer["firstname"],
                "lastname": customer["lastname"],
                "phone": customer["phone"],
            },
        )["id"]
    )


def create_sales_order(session: OAuth1Session, order: order.Order) -> str:
    return restlet.sales_order(session, "POST", body=order)["id"]


def build_customer_request(name: str, phone: str) -> customer.CustomerRequest:
    return {
        "leadsource": LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def build_prepared_customer(phone: str, name: str) -> customer.PreparedCustomer:
    return {
        "entity": None,
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }


def build_prepared_order_meta(memo: str) -> order.PreparedOrder:
    return {
        "leadsource": LEAD_SOURCE,
        "custbody_expecteddeliverytime": EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "memo": memo,
    }


O = TypeVar("O")


def build_prepared_order(
    builder: Callable[[Optional[O]], dict],
    data: Optional[O] = None,
) -> Callable[[Optional[dict]], order.PreparedOrder]:
    def build(prepared_order: Optional[dict] = {}) -> order.PreparedOrder:
        return (
            {
                **prepared_order,
                **builder(data),
            }
            if prepared_order
            else builder(data)
        )

    return build


def build_item(item: Optional[str], quantity: int, amount: int) -> order.Item:
    return (
        {
            "item": int(item),
            "quantity": quantity,
            "price": -1,
            "amount": int(amount / 1.1),
        }
        if item
        else {}
    )


def get_sales_order_url(id):
    return f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/app/accounting/transactions/salesord\.nl?id\={id}"
