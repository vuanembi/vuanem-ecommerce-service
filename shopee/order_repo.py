from datetime import datetime

from returns.result import safe
from google.cloud.firestore import DocumentReference

from shopee import shopee, shopee_repo

ORDER = shopee_repo.SHOPEE.collection("Order")


@safe
def create(order: shopee.Order) -> DocumentReference:
    doc_ref = ORDER.document(str(order["order_sn"]))
    doc_ref.set(order)
    return doc_ref


@safe
def get_max_updated_at() -> datetime:
    return shopee_repo.SHOPEE.get(["state.max_updated_at"]).get("state.max_updated_at")


@safe
def update_max_updated_at(orders: list[shopee.Order]) -> list[shopee.Order]:
    if orders:
        shopee_repo.SHOPEE.set(
            {
                "state": {
                    "max_created_at": max([order["create_time"] for order in orders]),
                    "max_updated_at": max([order["update_time"] for order in orders]),
                },
            },
            merge=True,
        )
    return orders
