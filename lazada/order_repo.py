from datetime import datetime

from returns.result import safe
from google.cloud.firestore import DocumentReference

from lazada import lazada, lazada_repo


ORDER = lazada_repo.LAZADA.collection("Order")


@safe
def create(order: lazada.OrderItems) -> DocumentReference:
    doc_ref = ORDER.document(str(order["order_id"]))
    doc_ref.set(order)
    return doc_ref


@safe
def get_max_updated_at() -> datetime:
    return (
        lazada_repo.LAZADA.get(["state.max_updated_at"])
        .get("state.max_updated_at")
        .replace(tzinfo=None)
    )


@safe
def update_max_updated_at(orders: list[lazada.OrderItems]) -> list[lazada.OrderItems]:
    if orders:
        lazada_repo.LAZADA.set(
            {
                "state": {
                    "max_created_at": max([order["created_at"] for order in orders]),
                    "max_updated_at": max([order["updated_at"] for order in orders]),
                },
            },
            merge=True,
        )
    return orders
