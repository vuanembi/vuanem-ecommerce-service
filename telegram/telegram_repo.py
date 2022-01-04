from typing import Callable
import os
import time

import requests

from telegram import telegram

BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"


def build_send_payload(builder: Callable, *args) -> telegram.PayloadBuilder:
    def build(payload: telegram.Payload) -> telegram.Payload:
        return {
            **payload,
            **builder(*args),
        }

    return build


def send(channel: telegram.Channel, payload_builder: telegram.PayloadBuilder) -> None:
    with requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload_builder({"chat_id": channel.chat_id, "parse_mode": "MarkdownV2"}),
    ) as r:
        if r.status_code == 429:
            time.sleep(3)
            return send(channel, payload_builder)
        else:
            r.raise_for_status()


def answer_callback(update: telegram.Update) -> None:
    requests.post(
        f"{BASE_URL}/answerCallbackQuery",
        json={
            "callback_query_id": update["callback_query"]["id"],
            "text": "Đợi xíu...",
        },
    )
