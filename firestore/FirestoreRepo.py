from typing import Callable, Optional, Any

from google.cloud import firestore
from google.cloud.firestore import (
    CollectionReference as ColRef,
    DocumentReference as DocRef,
)
from returns.result import ResultE, safe

FIRESTORE = firestore.Client()


def persist(
    collection: ColRef,
    factory: Callable[[Any], tuple[Optional[str], dict]],
) -> Callable[[Any], ResultE[DocRef]]:
    @safe
    def _persist(input_: Any) -> DocRef:
        id, data = factory(input_)
        doc_ref = collection.document(str(id)) if id else collection.document()
        doc_ref.create(data)
        return doc_ref

    return _persist


def get_one(col: ColRef) -> Callable[[str], ResultE[DocRef]]:
    @safe
    def get(id: str) -> DocRef:
        return col.document(str(id)).get()

    return get


def get_latest(col: ColRef, ts_key: str) -> Callable[[], ResultE[DocRef]]:
    @safe
    def get(*args) -> DocRef:
        return [
            i
            for i in col.order_by(ts_key, direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        ][0]

    return get


def update(col: ColRef, update_func: Callable[..., dict]) -> Callable[[str], str]:
    def _update(id: str) -> str:
        doc_ref = col.document(id)
        doc_ref.update(update_func(id))
        return doc_ref.id

    return _update


def delete(col: ColRef) -> Callable[[str], None]:
    def _delete(id: str) -> None:
        col.document(id).delete()

    return _delete
