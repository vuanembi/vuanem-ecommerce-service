import os

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, Failure
from returns.pipeline import flow
from returns.pointfree import lash, map_

from netsuite import netsuite, restlet, restlet_repo


def _get_customer(session: OAuth1Session):
    def _get(customer_req: netsuite.CustomerReq):
        return restlet_repo.request(
            session,
            restlet.Customer,
            "GET",
            params={
                "phone": customer_req["phone"],
            },
        )

    return _get


def _create_customer(session: OAuth1Session):
    def _create(customer_req: netsuite.CustomerReq):
        return restlet_repo.request(
            session,
            restlet.Customer,
            "POST",
            body={
                "leadsource": netsuite.LEAD_SOURCE,
                "firstname": customer_req["firstname"],
                "lastname": customer_req["lastname"],
                "phone": customer_req["phone"],
            },
        )

    return _create


def _add_order_meta(order: netsuite.PreparedOrder):
    def _add(customer: int) -> netsuite.Order:
        return {
            "entity": customer,
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
            "memo": order["memo"],
        }

    return _add


def _build_customer_request(name: str, phone: str) -> netsuite.CustomerReq:
    return {
        "leadsource": netsuite.LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def _get_or_create_customer(session: OAuth1Session):
    def _get(customer_req: netsuite.CustomerReq) -> ResultE[netsuite.Customer]:
        return flow(
            customer_req,
            _get_customer(session),
            lash(lambda _: Failure(customer_req)),
            lash(_create_customer(session)),
            map_(lambda x: x["id"]),
            map_(int),
        )

    return _get


def build_sales_order_from_prepared(session: OAuth1Session):
    def _build(order: netsuite.PreparedOrder) -> ResultE[netsuite.Order]:
        return flow(
            _build_customer_request(
                order["custbody_recipient"],
                order["custbody_customer_phone"],
            ),
            _get_or_create_customer(session),
            map_(_add_order_meta(order)),
        )

    return _build


def create_sales_order(session: OAuth1Session):
    def _create(order: netsuite.Order) -> str:
        return restlet_repo.request(
            session,
            restlet.SalesOrder,
            "POST",
            body=order,
        ).bind(lambda x: x["id"])

    return _create


def get_sales_order_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )
