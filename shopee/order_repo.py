from datetime import datetime

from returns.result import safe
from google.cloud.firestore import DocumentReference

from common.seller import Seller
from shopee import shopee

ORDER = "Order"


def create(seller: Seller):
    @safe
    def _create(order: shopee.Order) -> DocumentReference:
        doc_ref = seller.db.collection(ORDER).document(str(order["order_sn"]))
        doc_ref.set(order)
        return doc_ref

    return _create


@safe
def get_max_created_at(seller: Seller) -> datetime:
    max_created_at = "state.max_created_at"
    return seller.db.get([max_created_at]).get(max_created_at)


def update_max_created_at(seller: Seller):
    @safe
    def _update(orders: list[shopee.Order]) -> list[shopee.Order]:
        if orders:
            seller.db.set(
                {
                    "state": {
                        "max_created_at": max(
                            [order["create_time"] for order in orders]
                        ),
                    },
                },
                merge=True,
            )
        return orders

    return _update
