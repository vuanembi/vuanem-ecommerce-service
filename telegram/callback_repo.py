from typing import Callable
import json

from google.cloud import firestore
from returns.pipeline import pipe
from returns.pointfree import bind
from returns.result import Result, Success, Failure, safe

from google.cloud import firestore
from db.firestore import DB
from telegram import telegram

UPDATE = DB.document("Telegram").collection("Update")
CALLBACK = DB.document("Telegram").collection("Callback")


def _validate_unique(
    collection: firestore.CollectionReference,
    accessor: Callable[[telegram.Update], str],
):
    def _validate(update: telegram.Update) -> Result[telegram.Update, str]:
        id = str(accessor(update))
        if collection.document(id).get().exists:
            return Failure(f"Duplicate {collection.id}")
        else:
            collection.document(id).set(
                {
                    "update_id": update["update_id"],
                    "callback_query": {
                        "id": update["callback_query"]["id"],
                        "data": update["callback_query"]["data"],
                    },
                }
            )
            return Success(update)

    return _validate


validate_update = _validate_unique(UPDATE, lambda x: x["update_id"])
validate_callback = _validate_unique(CALLBACK, lambda x: x["callback_query"]["data"])

validate_data: Callable[[telegram.Update], Result[telegram.CalbackData, str]] = pipe(  # type: ignore
    lambda x: x["callback_query"]["data"],
    safe(json.loads),
    bind(
        lambda data: (
            Success(data)
            if set(data.keys()) == set(["a", "v", "t"])
            else Failure("Invalid data")
        )
    ),
)
