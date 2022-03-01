from returns.result import safe
from google.cloud.firestore import DocumentReference, CollectionReference

from tiki import tiki
from tiki.tiki_repo import TIKI


ORDER: CollectionReference = TIKI.collection("Order")


@safe
def create(order: tiki.Order) -> DocumentReference:
    doc_ref = ORDER.document(str(order["id"]))
    doc_ref.set(order)
    return doc_ref
