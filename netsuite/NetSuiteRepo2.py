import os

from typing import Callable, Optional, Any
from datetime import date

from requests.exceptions import HTTPError
from requests_oauthlib import OAuth1Session
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, lash
from returns.converters import result_to_maybe

from restlet.RestletRepo import sales_order, inventory_item, customer
from netsuite.NetSuite import (
    LEAD_SOURCE,
    EXPECTED_DELIVERY_TIME,
    CustomerReq,
    PreparedCustomer,
    Item,
    PreparedOrder,
    OrderMeta,
    Order,
)


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> Maybe[str]:
    return result_to_maybe(
        inventory_item(
            session,
            "GET",
            params={
                "itemid": sku,
            },
        )
    ).bind(lambda x: x["id"])


def get_customer(session, customer_req):
    def _get():
        return customer(
            session,
            "GET",
            params={
                "phone": customer_req["phone"],
            },
        ).bind(lambda x: x["id"])

    return _get


def create_customer(session, customer_req):
    def _create():
        return customer(
            session,
            "POST",
            body={
                "leadsource": LEAD_SOURCE,
                "firstname": customer_req["firstname"],
                "lastname": customer_req["lastname"],
                "phone": customer_req["phone"],
            },
        ).bind(lambda x: x["id"])

    return _create


def get_customer_if_not_exist(
    session: OAuth1Session,
    customer_req: CustomerReq,
) -> str:
    return get_customer(session, customer_req).lash(
        create_customer(session, customer_req)
    )


def create_sales_order(session: OAuth1Session, order: Order) -> str:
    return sales_order(session, "POST", body=order)["id"]


def build_customer_request(name: str, phone: str) -> CustomerReq:
    return {
        "leadsource": LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def build_prepared_customer(phone: str, name: str) -> PreparedCustomer:
    return {
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }


def build_prepared_order_meta(memo: str) -> OrderMeta:
    return {
        "leadsource": LEAD_SOURCE,
        "custbody_expecteddeliverytime": EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "memo": memo,
    }


def build_prepared_order(
    builder: Callable[[Any], dict],
    data: Optional[Any] = None,
) -> Callable[[dict], PreparedOrder]:
    def build(prepared_order: dict = {}) -> PreparedOrder:
        return {
            **prepared_order,
            **builder(data),
        }

    return build


def build_item(item: Optional[str], quantity: int, amount: int) -> Item:
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


def get_sales_order_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )


def build_sales_order_from_prepared(
    session: OAuth1Session,
    order: PreparedOrder,
) -> Order:
    return {
        "entity": int(
            get_customer_if_not_exist(
                session,
                build_customer_request(
                    order["custbody_recipient"], order["custbody_customer_phone"]
                ),
            )
        ),
        "trandate": order["trandate"],
        "subsidiary": order["subsidiary"],
        "location": order["location"],
        "department": order["department"],
        "custbody_customer_phone": order["custbody_customer_phone"],
        "custbody_expecteddeliverytime": order["custbody_expecteddeliverytime"],
        "custbody_recipient": order["custbody_recipient"],
        "custbody_recipient_phone": order["custbody_recipient_phone"],
        "shippingaddress": order["shippingaddress"],
        "custbody_order_payment_method": order["custbody_order_payment_method"],
        "salesrep": order["salesrep"],
        "leadsource": order["leadsource"],
        "partner": order["partner"],
        "custbody_onl_rep": order["custbody_onl_rep"],
        "item": [
            {
                "item": i["item"],
                "quantity": i["quantity"],
                "price": i["price"],
                "amount": i["amount"],
            }
            for i in order["item"]
        ],
    }
