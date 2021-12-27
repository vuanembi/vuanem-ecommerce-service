from typing import Callable
import os
import time

import requests

from telegram import telegram

BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
CHAT_ID = "-1001685563275" if os.getenv("PYTHON_ENV") == "prod" else "-645664226"


def build_send_payload(builder: Callable, *args) -> telegram.PayloadBuilder:
    def build(payload: telegram.Payload) -> telegram.Payload:
        return {
            **payload,
            **builder(*args),
        }

    return build


def send(payload_builder: telegram.PayloadBuilder) -> dict:
    with requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload_builder({"chat_id": CHAT_ID, "parse_mode": "MarkdownV2"}),
    ) as r:
        if r.status_code == 429:
            time.sleep(3)
            return send(payload_builder)
        else:
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