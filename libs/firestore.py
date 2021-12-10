from typing import Callable, Optional, Any
import os

from google.cloud import firestore

from models.netsuite import order

FIRESTORE = firestore.Client()

TIKI_ACKS = FIRESTORE.collection(
    "TikiAcks" if os.getenv("PYTHON_ENV") == "prod" else "TikiAcks-dev"
)
PREPARED_ORDERS = FIRESTORE.collection(
    "PreparedOrders" if os.getenv("PYTHON_ENV") == "prod" else "PreparedOrders-dev"
)
TELEGRAM_UPDATES = FIRESTORE.collection(
    "TelegramUpdates" if os.getenv("PYTHON_ENV") == "prod" else "TelegramUpdates-dev"
)


def _create(
    collection: firestore.CollectionReference,
    factory: Callable[[Any], tuple[Optional[str], dict]],
) -> Callable[[Any], str]:
    def create(input_) -> str:
        id, data = factory(input_)
        doc_ref = collection.document(str(id)) if id else collection.document()
        doc_ref.create(data)
        return doc_ref.id

    return create


def _get_one_by_id(
    collection: firestore.CollectionReference,
) -> Callable[[str], firestore.DocumentReference]:
    def get(id: str) -> firestore.DocumentReference:
        return collection.document(str(id)).get()

    return get


def _get_latest(
    collection: firestore.CollectionReference,
    timestamp_col: str,
) -> Callable[[], Optional[str]]:
    def get() -> Optional[str]:
        try:
            return [
                i
                for i in collection.order_by(
                    timestamp_col, direction=firestore.Query.DESCENDING
                )
                .limit(1)
                .get()
            ][0].id
        except IndexError:
            return None

    return get


def _delete(
    collection: firestore.CollectionReference,
):
    def delete(id):
        collection.document(id).delete()

    return delete


create_tiki_ack_id: Callable[[str], str] = _create(
    TIKI_ACKS,
    lambda ack_id: (
        str(ack_id),
        {
            "created_at": firestore.SERVER_TIMESTAMP,
        },
    ),
)
get_latest_tiki_ack_id = _get_latest(TIKI_ACKS, "created_at")
delete_tiki_ack_id = _delete(TIKI_ACKS)


create_prepared_order: Callable[[order.PreparedOrder], str] = _create(
    PREPARED_ORDERS,
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
get_prepared_order: Callable[[str], firestore.DocumentReference] = _get_one_by_id(
    PREPARED_ORDERS
)


create_telegram_update: Callable[[dict], str] = _create(
    TELEGRAM_UPDATES,
    lambda update: (
        update["update_id"],
        {
            "update": {
                "update_id": update["update_id"],
                "callback_query": {
                    "id": update["callback_query"]["id"],
                    "data": update["callback_query"]["data"],
                },
            },
            "created_at": firestore.SERVER_TIMESTAMP,
        },
    ),
)
get_telegram_update: Callable[[str], firestore.DocumentReference] = _get_one_by_id(
    TELEGRAM_UPDATES
)
