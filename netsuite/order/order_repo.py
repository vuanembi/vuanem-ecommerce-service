from returns.result import Result, ResultE, Success, Failure, safe
from google.cloud.firestore import DocumentReference, SERVER_TIMESTAMP

from netsuite.order import order
from db.firestore import DB

ORDER = DB.document("NetSuite").collection("Order")


@safe
def create(order: order.Order) -> DocumentReference:
    doc_ref = ORDER.document()
    doc_ref.create(
        {
            "source": order["source"],
            "order": order["order"],
            "status": "pending",
            "transaction_id": None,
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
        order_doc_ref.set(
            {
                "status": status,
                "order.id": id,
            },
            merge=True,
        )
        return id, order_doc_ref.get(["order.memo"]).get("order.memo")

    return _update
