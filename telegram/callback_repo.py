from typing import Callable
import json
from datetime import datetime

from google.cloud import firestore
from returns.pipeline import flow
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
                    "created_at": datetime.utcnow(),
                }
            )
            return Success(update)

    return _validate


validate_update = _validate_unique(UPDATE, lambda x: x["update_id"])
validate_callback = _validate_unique(CALLBACK, lambda x: x["callback_query"]["data"])


def validate_data(
    update: telegram.Update,
) -> Result[tuple[str, int, telegram.CalbackData], str]:
    return flow(
        update,
        lambda x: x["callback_query"]["data"],
        safe(json.loads),
        bind(  # type: ignore
            lambda data: (
                Success(  # type: ignore
                    (
                        str(update["callback_query"]["message"]["chat"]["id"]),
                        update["callback_query"]["message"]["message_id"],
                        data,
                    )
                )
                if set(data.keys()) == set(["a", "v", "t"])  # type: ignore
                else Failure("Invalid data")
            )
        ),
    )
