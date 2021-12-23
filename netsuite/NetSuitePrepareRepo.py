import os

from typing import Callable, Optional, Any
from datetime import date

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, Success
from google.cloud import firestore  # type: ignore


from netsuite import NetSuite, Restlet, RestletRepo
from db.firestore import FIRESTORE, persist

collection = FIRESTORE.collection(
    "PreparedOrders" if os.getenv("PYTHON_ENV") == "prod" else "PreparedOrders-dev"
)


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> ResultE[str]:
    return (
        RestletRepo.request(
            session,
            Restlet.InventoryItem,
            "GET",
            params={"itemid": sku},
        )
        .bind(lambda x: Success(x["id"]))
        .lash(lambda _: Success(None))
    )


def build_prepared_customer(phone: str, name: str) -> NetSuite.PreparedCustomer:
    return {
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }


def build_item(item: Optional[str], quantity: int, amount: int) -> NetSuite.Item:
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


def build_prepared_order_meta(memo: str) -> NetSuite.OrderMeta:
    return {
        "leadsource": NetSuite.LEAD_SOURCE,
        "custbody_expecteddeliverytime": NetSuite.EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "memo": memo,
    }


def build_prepared_order(
    builder: Callable[[Any], dict],
    data: Optional[Any] = None,
) -> Callable[[dict], NetSuite.PreparedOrder]:
    def build(prepared_order: dict = {}) -> NetSuite.PreparedOrder:
        return {
            **prepared_order,
            **builder(data),
        }

    return build


persist_prepared_order: Callable[
    [NetSuite.PreparedOrder],
    ResultE[firestore.DocumentReference],
] = persist(
    collection,
    lambda order: (
        None,
        {
            "order": order,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
    ),
)
