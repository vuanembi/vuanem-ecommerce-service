from datetime import datetime

from returns.result import safe
from google.cloud.firestore import DocumentReference

from common.seller import Seller
from lazada import lazada

ORDER = "Order"


def create(seller: Seller):
    @safe
    def _create(order: lazada.OrderItems) -> DocumentReference:
        doc_ref = seller.db.collection(ORDER).document(str(order["order_id"]))
        doc_ref.set(order)
        return doc_ref

    return _create


@safe
def get_max_created_at(seller: Seller) -> datetime:
    max_created_at = "state.max_created_at"
    return seller.db.get([max_created_at]).get(max_created_at).replace(tzinfo=None)


def update_max_created_at(seller: Seller) -> list[lazada.OrderItems]:
    @safe
    def _update(orders: list[lazada.OrderItems]) -> list[lazada.OrderItems]:
        if orders:
            seller.db.set(
                {
                    "state": {
                        "max_created_at": max(
                            [order["created_at"] for order in orders]
                        ),
                    },
                },
                merge=True,
            )
        return orders

    return _update
