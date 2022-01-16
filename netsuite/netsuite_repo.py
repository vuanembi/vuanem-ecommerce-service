from typing import Union
import os

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, Success, Failure
from returns.pipeline import flow
from returns.pointfree import lash, map_

from netsuite import netsuite, restlet, restlet_repo




def _get_customer(session: OAuth1Session):
    def _get(customer_req: netsuite.CustomerReq) -> ResultE[dict[str, str]]:
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
    def _create(customer_req: netsuite.CustomerReq) -> ResultE[dict[str, str]]:
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
            "shipdate": order["shipdate"],
            "subsidiary": order["subsidiary"],
            "location": order["location"],
            "department": order["department"],
            "custbody_customer_phone": order["custbody_customer_phone"],
            "custbody_expecteddeliverytime": order["custbody_expecteddeliverytime"],
            "custbody_recipient": order["custbody_recipient"],
            "custbody_recipient_phone": order["custbody_recipient_phone"],
            "shippingaddress": order["shippingaddress"],
            "custbody_order_payment_method": order["custbody_order_payment_method"],
            "custbody_expected_shipping_method": order[
                "custbody_expected_shipping_method"
            ],
            "custbody_print_form": order["custbody_print_form"],
            "memo": order["memo"],
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
                    "commitinventory": i["commitinventory"],
                    "location": i["location"],
                    "custcol_deliver_location": i["custcol_deliver_location"],
                }
                for i in order["item"]
            ],
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
    def _get(order: netsuite.PreparedOrder) -> ResultE[int]:
        customer_req = _build_customer_request(
            order["custbody_recipient"],
            order["custbody_customer_phone"],
        )
        return flow(
            customer_req,
            _get_customer(session),
            lash(lambda _: Failure(customer_req)),  # type: ignore
            lash(_create_customer(session)),
            map_(lambda x: x["id"]),  # type: ignore
            map_(int),
        )

    return _get


def build_sales_order_from_prepared(session: OAuth1Session):
    def _build(
        order: Union[netsuite.PreparedOrder, netsuite.Order]
    ) -> ResultE[netsuite.Order]:
        return flow(
            order,
            lambda x: Success(x["entity"]) if "entity" in x else Failure(order),
            lash(_get_or_create_customer(session)),
            map_(_add_order_meta(order)),
        )

    return _build


def create_sales_order(session: OAuth1Session):
    def _create(order: netsuite.Order) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.SalesOrder,
            "POST",
            body={**order},
        )

    return _create


def close_sales_order(session: OAuth1Session):
    def _delete(order_id: int) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.SalesOrder,
            "DELETE",
            params={"id": order_id},
        )

    return _delete


def get_sales_order_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )
