from returns.result import Result, ResultE, Success, Failure, safe
from google.cloud.firestore import DocumentReference, SERVER_TIMESTAMP

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
        existing_ref.set(
            {
                "updated_at": SERVER_TIMESTAMP,
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
                "created_at": SERVER_TIMESTAMP,
                "updated_at": SERVER_TIMESTAMP,
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
    def _update(id: int) -> tuple[int, str]:
        order_doc_ref.update(
            {
                "status": status,
                "order.id": id,
                "updated_at": SERVER_TIMESTAMP,
            },
        )
        return id, order_doc_ref.get(["order.memo"]).get("order.memo")

    return _update
