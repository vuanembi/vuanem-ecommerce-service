from typing import Any, Callable, TypeVar

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google import auth

from models.netsuite import order

_, PROJECT_ID = auth.default()
firebase_admin.initialize_app(
    credentials.ApplicationDefault(),
    {
        "projectId": PROJECT_ID,
    },
)

FIRESTORE_DB = firestore.client()

D = TypeVar("D")


def add_doc(
    collection: str,
    template: Callable[[D], dict[str, Any]],
) -> Callable[[D], str]:
    def add(data: D) -> str:
        _, doc_ref = FIRESTORE_DB.collection(collection).add(template(data))
        return doc_ref.id

    return add


add_ack: Callable[[str], str] = add_doc(
    "TikiAcks",
    lambda ack_id: {
        "ack_id": ack_id,
        "timestamp": firestore.SERVER_TIMESTAMP,
    },
)

add_prepared_order: Callable[[order.PreparedOrder], str] = add_doc(
    "PreparedOrders",
    lambda x: {
        "order": x,
        "status": "added",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    },
)


def get_latest_ack_id() -> str:
    return [
        i.to_dict()
        for i in FIRESTORE_DB.collection("TikiAcks")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    ][0]["ack_id"]
