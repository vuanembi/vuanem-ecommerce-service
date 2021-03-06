from datetime import datetime

from returns.result import Result, ResultE, Success, Failure, safe
from google.cloud.firestore import DocumentReference

from netsuite.order import order
from netsuite.sales_order import sales_order
from db.firestore import DB

ORDER = DB.document("NetSuite").collection("Order")


@safe
def create(
    built_order: tuple[DocumentReference, sales_order.Order]
) -> DocumentReference:
    source_ref, order = built_order
    existing = ORDER.where("source_ref", "==", source_ref).get()
    if existing:
        existing_ref = existing[0].reference
        existing_ref.update(
            {
                "updated_at": datetime.utcnow(),
            }
        )
        return existing_ref
    else:
        doc_ref = ORDER.document()
        doc_ref.create(
            {
                "source_ref": source_ref,
                "order": order,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_deleted": False,
            },
        )
        return doc_ref


def get(id: str) -> ResultE[DocumentReference]:
    doc_ref = ORDER.document(id)
    if doc_ref.get().exists:
        return Success(doc_ref)
    else:
        return Failure(Exception("{id} does not exist"))


def validate(status: str):
    def _validate(order: order.Order) -> Result[order.Order, str]:
        return (
            Success(order)
            if order["status"] == status
            else Failure(f"Wrong status, expected {status}, got {order['status']}")
        )

    return _validate


def update(order_doc_ref: DocumentReference, status: str):
    @safe
    def _update(id: int) -> DocumentReference:
        order_doc_ref.update(
            {
                "status": status,
                "order.id": id,
                "updated_at": datetime.utcnow(),
            },
        )
        return order_doc_ref

    return _update
