from typing import Callable
import os
import requests

from telegram.Telegram import Payload, PayloadBuilder

BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
CHAT_ID = "-1001685563275" if os.getenv("PYTHON_ENV") == "prod" else "-645664226"


def build_send_payload(builder: Callable, *args) -> PayloadBuilder:
    def build(payload: Payload) -> Payload:
        return {
            **payload,
            **builder(*args),
        }

    return build


def send(payload_builder: PayloadBuilder) -> dict:
    with requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload_builder({"chat_id": CHAT_ID, "parse_mode": "MarkdownV2"}),
    ) as r:
        r.raise_for_status()
        return r.json()


def answer_callback(callback_query_id: str) -> None:
    requests.post(
        f"{BASE_URL}/answerCallbackQuery",
        json={
            "callback_query_id": callback_query_id,
            "text": "Đợi xíu...",
        },
    )
