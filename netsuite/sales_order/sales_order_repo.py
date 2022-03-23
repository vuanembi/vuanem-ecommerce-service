from typing import Optional
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
            **order,  # type: ignore
        }

    return _add


def build(session: OAuth1Session):
    def _build(order: sales_order.Order) -> ResultE[sales_order.Order]:
        return flow(
            order,
            lambda x: (x["custbody_recipient"], x["custbody_recipient_phone"]),
            customer_repo.build(session),
            map_(_build_customer_callback(order)),
        )

    return _build


def create(session: OAuth1Session):
    def _create(order: sales_order.Order) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.Record,
            "POST",
            body={
                "type": "salesorder",
                "data": order,
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


def get_url(id: Optional[int]) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/"
        + f"app/accounting/transactions/salesord\.nl?id\={id}"
    )
