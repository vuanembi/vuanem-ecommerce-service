from typing import Any, Optional, Union
import os
import json

import yaml
import requests

from libs import tiki
from models import telegram

CHAT_ID = "-645664226"
DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def get_chat_id(update: telegram.Update) -> Optional[int]:
    return update.get("callback_query", {}).get("message", {}).get("chat", {}).get("id")


def filter_chat_id(update: telegram.Update) -> bool:
    return True if str(get_chat_id(update)) == CHAT_ID else False


def get_callback_query_data(update: telegram.Update) -> dict:
    return (
        json.loads(update["callback_query"].get("data"))
        if filter_chat_id(update)
        else None
    )


def send_telegram(text: str, reply_markup: Optional[dict] = None) -> dict:
    payload: dict[str, Any] = {
        "chat_id": CHAT_ID,
        "parse_mode": "MarkdownV2",
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    with requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json=payload,
    ) as r:
        return r.json()


def send_new_order(
    ecommerce: str,
    order: Union[tiki.Order, None],
    prepared_order,
) -> dict:
    return send_telegram(
        "\n".join(
            [
                f"Đơn hàng *{ecommerce}* mới",
                DIVIDER,
                "```",
                yaml.dump(order, allow_unicode=True),
                "```",
            ]
        ),
        {
            "inline_keyboard": [
                [
                    {"text": "Tạo đơn", "callback_data": json.dumps(prepared_order)},
                    {"text": "Huỷ đơn", "callback_data": json.dumps(prepared_order)},
                ]
            ]
        },
    )


def get_sales_order_url(id):
    return f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/app/accounting/transactions/salesord\.nl?id\={id}"


def send_created_order(ecommerce: str, id: str) -> dict:
    return send_telegram(
        "\n".join(
            [
                f"Tạo dơn hàng *{ecommerce}* thành công ^^",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    )


def send_error_create_order(ecommerce: str, error: Exception, order_ids: list[str]):
    return send_telegram(
        "\n".join(
            [
                f"Tạo đơn hàng *{ecommerce}* thất bại: {','.join(order_ids)}",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    )
