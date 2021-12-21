from typing import Optional, Callable
import os

from requests import Session
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from returns.io import IOResultE, impure_safe

from firestore.FirestoreRepo import get_latest, create
from tiki.Tiki import Order, EventRes

BASE_URL = "https://api.tiki.vn/integration"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('TIKI_ACCESS_TOKEN')}",
    "User-Agent": "PostmanRuntime/7.28.3",
}
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)

@impure_safe
def get_new_access_token():
    return OAuth2Session(
        client=BackendApplicationClient(client_id=os.getenv("TIKI_CLIENT_ID"))
    ).fetch_token(
        token_url="https://provider.com/oauth2/token",
        client_id=os.getenv("TIKI_CLIENT_ID"),
        client_secret=os.getenv("TIKI_CLIENT_SECRET"),
    )


def get_events(session: Session) -> Callable[[Optional[str]], IOResultE[EventRes]]:
    @impure_safe
    def _get(ack_id: Optional[str] = None) -> EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull",
            json={"ack_id": ack_id},
            headers=HEADERS,
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get


def get_order(session: Session) -> Callable[[str], IOResultE[Order]]:
    @impure_safe
    def _get(order_id: str) -> Order:
        with session.get(
            f"{BASE_URL}/v2/orders/{order_id}",
            params={"include": "items.fees"},
            headers=HEADERS,
        ) as r:
            data = r.json()
        return {
            "id": data["id"],
            "code": data["code"],
            "items": [
                {
                    "product": {
                        "name": item["product"]["name"],
                        "seller_product_code": item["product"]["seller_product_code"],
                    },
                    "qty": item["qty"],
                    "invoice": {
                        "row_total": item["invoice"]["row_total"],
                    },
                }
                for item in data["items"]
            ],
            "shipping": {
                "address": {
                    "full_name": data["shipping"]["address"]["full_name"],
                    "street": data["shipping"]["address"]["street"],
                    "ward": data["shipping"]["address"]["ward"],
                    "district": data["shipping"]["address"]["district"],
                    "phone": data["shipping"]["address"]["phone"],
                },
            },
        }

    return _get
