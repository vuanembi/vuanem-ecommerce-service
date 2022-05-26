from datetime import datetime

from returns.result import safe

from db.firestore import DB

TIKI = DB.document("Tiki")


@safe
def get_ack_id() -> str:
    return TIKI.get(["state.ack.ack_id"]).get("state.ack.ack_id")


@safe
def update_ack_id(ack_id: str) -> str:
    TIKI.set(
        {
            "state": {
                "ack": {
                    "ack_id": ack_id,
                    "updated_at": datetime.utcnow(),
                }
            },
            "test": datetime.utcnow(),
        },
        merge=True,
    )
    return ack_id
