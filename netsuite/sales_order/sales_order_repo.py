from datetime import date, timedelta
import os

from requests_oauthlib import OAuth1Session
from returns.result import ResultE
from returns.pipeline import flow
from returns.pointfree import map_

from netsuite.sales_order import sales_order
from netsuite.customer import customer, customer_repo
from netsuite.restlet import restlet, restlet_repo


def build_detail(memo: str) -> sales_order.Detail:
    return {
        "id": None,
        "leadsource": customer.LEAD_SOURCE,
        "custbody_expecteddeliverytime": sales_order.EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "shipdate": (date.today() + timedelta(days=3)).isoformat(),
        "custbody_expected_shipping_method": sales_order.CUSTBODY_EXPECTED_SHIPPING_METHOD,
        "custbody_print_form": sales_order.CUSTBODY_PRINT_FORM,
        "memo": memo,
    }


def _build_customer_callback(order: sales_order.Order):
    def _add(customer_id: int) -> sales_order.Order:
        return {
            "entity": customer_id,
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


def build(session: OAuth1Session):
    def _build(order: sales_order.Order) -> ResultE[sales_order.Order]:
        return flow(
            order,
            customer_repo.build(session),
            map_(_build_customer_callback(order)),
        )

    return _build


def create(session: OAuth1Session):
    def _create(order: sales_order.Order) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.SalesOrder,
            "POST",
            body={
                **order,
            },
        )

    return _create


def close(session: OAuth1Session):
    def _delete(order_id: int) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.SalesOrder,
            "DELETE",
            params={
                "id": order_id,
            },
        )

    return _delete


def get_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )
