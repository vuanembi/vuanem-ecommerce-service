import os

from requests_oauthlib import OAuth1Session
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, lash
from returns.converters import result_to_maybe

from netsuite import NetSuite, Restlet, RestletRepo

# from restlet.RestletRepo import sales_order, inventory_item, customer
# from netsuite.NetSuite import (
#     LEAD_SOURCE,
#     CustomerReq,
#     PreparedOrder,
#     Order,
# )


def get_customer(session, customer_req):
    def _get():
        return RestletRepo.request(
            session,
            Restlet.Customer,
            "GET",
            params={
                "phone": customer_req["phone"],
            },
        ).bind(lambda x: x["id"])

    return _get


def create_customer(session, customer_req):
    def _create():
        return RestletRepo.request(
            session,
            Restlet.Customer,
            "POST",
            body={
                "leadsource": NetSuite.LEAD_SOURCE,
                "firstname": customer_req["firstname"],
                "lastname": customer_req["lastname"],
                "phone": customer_req["phone"],
            },
        ).bind(lambda x: x["id"])

    return _create


def get_customer_if_not_exist(
    session: OAuth1Session,
    customer_req: NetSuite.CustomerReq,
) -> str:
    return get_customer(session, customer_req).lash(
        create_customer(session, customer_req)
    )


def build_customer_request(name: str, phone: str) -> NetSuite.CustomerReq:
    return {
        "leadsource": NetSuite.LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def get_sales_order_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )


def build_sales_order_from_prepared(
    session: OAuth1Session,
    order: NetSuite.PreparedOrder,
) -> NetSuite.Order:
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


def create_sales_order(session: OAuth1Session, order: NetSuite.Order) -> str:
    return RestletRepo.request(session, Restlet.SalesOrder, "POST", body=order)["id"]
