import os

from typing import Callable, Optional, Any
from datetime import date
from google.cloud.firestore_v1.document import DocumentReference

from requests_oauthlib import OAuth1Session
from returns.io import IOSuccess, IOResultE
from google.cloud import firestore


from restlet.RestletRepo import inventory_item
from netsuite.NetSuite import (
    LEAD_SOURCE,
    EXPECTED_DELIVERY_TIME,
    PreparedCustomer,
    Item,
    PreparedOrder,
    OrderMeta,
)
from firestore.FirestoreRepo import FIRESTORE, persist

collection = FIRESTORE.collection(
    "PreparedOrders" if os.getenv("PYTHON_ENV") == "prod" else "PreparedOrders-dev"
)


def map_sku_to_item_id(session: OAuth1Session, sku: str):
    return (
        inventory_item(
            session,
            "GET",
            params={
                "itemid": sku,
            },
        )
        .bind(lambda x: IOSuccess(x["id"]))
        .lash(lambda _: IOSuccess(None))
        .bind(lambda x: x)
    )


def build_prepared_customer(phone: str, name: str) -> PreparedCustomer:
    return {
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }


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


persist_prepared_order: Callable[
    [PreparedOrder], IOResultE[DocumentReference]
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
