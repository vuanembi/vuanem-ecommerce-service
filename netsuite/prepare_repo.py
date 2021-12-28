from typing import Callable, Optional, Any
from datetime import date

from requests_oauthlib import OAuth1Session
from returns.result import Result, ResultE, Success, Failure, safe
from google.cloud import firestore


from netsuite import netsuite, restlet, restlet_repo
from db.firestore import DB

PREPARED_ORDER = DB.document("NetSuite").collection("PreparedOrder")


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> ResultE[str]:
    return (
        restlet_repo.request(
            session,
            restlet.InventoryItem,
            "GET",
            params={"itemid": sku},
        )
        .bind(lambda x: Success(x["id"]))
        .lash(lambda _: Failure(None))
    )


def build_item(
    session: OAuth1Session,
    sku: str,
    qty: int,
    amt: int,
) -> ResultE[netsuite.Items]:
    return map_sku_to_item_id(session, sku).bind(
        lambda x: Success(
            {
                "item": int(x),
                "quantity": qty,
                "price": -1,
                "amount": int(amt / 1.1),
            }
        )
    )


def build_customer(phone: str, name: str) -> netsuite.PreparedCustomer:
    return {
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }

def build_prepared_order_meta(memo: str) -> netsuite.OrderMeta:
    return {
        "leadsource": netsuite.LEAD_SOURCE,
        "custbody_expecteddeliverytime": netsuite.EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "memo": memo,
    }


def build_prepared_order(builder, data=None):
    def build(prepared_order: dict = {}):
        return {
            **prepared_order,
            **builder(data),
        }

    return build


@safe
def persist_prepared_order(
    order: netsuite.PreparedOrder,
) -> firestore.DocumentReference:
    doc_ref = PREPARED_ORDER.document()
    doc_ref.create(
        {
            "order": order,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
    )
    return doc_ref


def get_prepared_order(id: str) -> Result[firestore.DocumentReference, str]:
    doc_ref = PREPARED_ORDER.document(id).get()
    if doc_ref.exists:
        return Success(doc_ref)
    else:
        return Failure("{id} does not exist")


def validate_prepared_order(status: str):
    def _validate(order: dict) -> Result[netsuite.PreparedOrder, str]:
        return (
            Success(order["order"])
            if order["status"] == status
            else Failure(f"Wrong status, expected {status}, got {order['status']}")
        )

    return _validate
