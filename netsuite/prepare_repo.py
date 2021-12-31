from typing import Optional, Union
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
        .map(lambda x: x["id"])  # type: ignore
        .lash(lambda _: Failure(Exception()))
    )


def build_item(
    session: OAuth1Session,
    sku: str,
    qty: int,
    amt: int,
    location: int,
) -> ResultE[netsuite.Item]:
    return map_sku_to_item_id(session, sku).map(
        lambda x: {
            "item": int(x),
            "quantity": qty,
            "price": -1,
            "amount": int(amt / 1.1),
            "commitinventory": netsuite.COMMIT_INVENTORY,
            "location": location,
            # ! hardcoded
            "custcol_deliver_location": netsuite.CUSTCOL_DELIVER_LOCATION,
        }
    )


def build_customer(
    default: netsuite.PreparedCustomer,
    phone: Optional[str] = None,
    name: Optional[str] = None,
) -> netsuite.PreparedCustomer:
    return (
        {
            "custbody_customer_phone": phone,
            "custbody_recipient_phone": phone,
            "custbody_recipient": name,
            "shippingaddress": {
                "addressee": name,
            },
        }
        if phone and name
        else default
    )


def build_prepared_order_meta(memo: str) -> netsuite.OrderMeta:
    return {
        "leadsource": netsuite.LEAD_SOURCE,
        "custbody_expecteddeliverytime": netsuite.EXPECTED_DELIVERY_TIME,
        "trandate": date.today().isoformat(),
        "custbody_expected_shipping_method": netsuite.CUSTBODY_EXPECTED_SHIPPING_METHOD,
        "custbody_print_form": netsuite.CUSTBODY_PRINT_FORM,
        "memo": memo,
    }


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
    doc_ref = PREPARED_ORDER.document(id)
    if doc_ref.get().exists:
        return Success(doc_ref)
    else:
        return Failure("{id} does not exist")


def validate_prepared_order(status: str):
    def _validate(
        order: dict,
    ) -> Result[Union[netsuite.PreparedOrder, netsuite.Order], str]:
        return (
            Success(order["order"])
            if order["status"] == status
            else Failure(f"Wrong status, expected {status}, got {order['status']}")
        )

    return _validate


def update_prepared_order_status(doc_ref: firestore.DocumentReference, status: str):
    def _update(id: int) -> int:
        doc_ref.set(
            {
                "status": status,
                "transactionId": id,
            },
            merge=True,
        )
        return id

    return _update
