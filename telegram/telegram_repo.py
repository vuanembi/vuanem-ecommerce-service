import os
import time
import json
import io

import requests

from telegram import telegram

BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"


def build_callback_data(type_: str, action: int, value: str) -> str:
    return json.dumps(
        {
            "t": type_,
            "a": action,
            "v": value,
        }
    )


def sendMessage(payload: telegram.Payload) -> None:
    with requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "parse_mode": "MarkdownV2",
            **payload,
        },
    ) as r:
        if r.status_code == 429:
            time.sleep(3)
            return sendMessage(payload)
        else:
            r.raise_for_status()


def sendDocuments(
    payload: telegram.Payload,
    files: list[tuple[str, tuple[str, io.BytesIO, str]]],
) -> None:
    with requests.post(
        f"{BASE_URL}/sendDocument",
        params={**payload},
        files=files,  # type: ignore
    ) as r:
        if r.status_code == 429:
            time.sleep(3)
            return sendMessage(payload)
        else:
            r.raise_for_status()


def answer_callback(update: telegram.Update) -> telegram.Update:
    requests.post(
        f"{BASE_URL}/answerCallbackQuery",
        json={
            "callback_query_id": update["callback_query"]["id"],
            "text": "Đợi xíu...",
        },
    )
    return update
