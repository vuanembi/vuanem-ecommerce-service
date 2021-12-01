import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google import auth

_, PROJECT_ID = auth.default()
firebase_admin.initialize_app(
    credentials.ApplicationDefault(),
    {
        "projectId": PROJECT_ID,
    },
)

FIRESTORE_DB = firestore.client()
COLLECTION = FIRESTORE_DB.collection("TikiAcks")


def add_ack(ack_id: str) -> str:
    _, doc_ref = COLLECTION.add(
        {
            "ack_id": ack_id,
            "timestamp": firestore.SERVER_TIMESTAMP,
        }
    )
    return doc_ref.id


def get_latest_ack_id() -> str:
    return [
        i.to_dict()
        for i in COLLECTION.order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    ][0]["ack_id"]
