import requests

from libs.firestore import add_ack, get_latest_ack_id
from libs.tiki import pull_events, get_order
from libs.telegram import send_tiki_order


def handle_event_queue() -> dict:
    with requests.Session() as session:
        ack_id, events = pull_events(session, get_latest_ack_id())
        return {
            "controller": "tiki",
            "results": {
                "telegram_msg": len(
                    [
                        send_tiki_order(order)
                        for order in [
                            get_order(session, event["payload"]["order_code"])
                            for event in events
                        ]
                    ]
                )
                if events
                else None,
                "ack_id": add_ack(ack_id),
            },
        }
