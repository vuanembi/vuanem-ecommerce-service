from datetime import datetime

from returns.result import safe
from google.cloud.firestore import DocumentReference

from db.firestore import DB
from shopee import shopee

SHOPEE = DB.document("Shopee")
ORDER = SHOPEE.collection("Order")


@safe
def create(order: shopee.Order) -> DocumentReference:
    doc_ref = ORDER.document(str(order["order_sn"]))
    doc_ref.create(order)
    return doc_ref


@safe
def get_max_created_at() -> datetime:
    return SHOPEE.get(["state.max_created_at"]).get("state.max_created_at")


@safe
def update_max_created_at(orders: list[shopee.Order]) -> list[shopee.Order]:
    if orders:
        SHOPEE.set(
            {
                "state": {
                    "max_created_at": max([order["create_time"] for order in orders]),
                },
            },
            merge=True,
        )
    return orders
