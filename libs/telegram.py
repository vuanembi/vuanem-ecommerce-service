from typing import Optional, Union
import os
import json

import yaml
import requests

from libs import tiki
from models import telegram

CHAT_ID = "-645664226"

def get_chat_id(update: telegram.Update) -> Optional[int]:
    return update.get("callback_query", {}).get("message", {}).get("chat", {}).get("id")

def filter_chat_id(update: telegram.Update) -> bool:
    return True if str(get_chat_id(update)) == CHAT_ID else False

def get_callback_query_data(update: telegram.Update) -> dict:
    return json.loads(update["callback_query"].get("data")) if filter_chat_id(update) else None

divider = "\=\=\=\=\=\=\=\=\=\=\="

def send_telegram(text: str) -> dict:
    with requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "parse_mode": "MarkdownV2",
            "reply_markup": {
                "keyboard": [
                    [
                        {
                            "text": "Đã Nhận thông tin",
                        },
                        {
                            "text": "Đã Check đơn trên NetSuite",
                        },
                    ],
                ]
            },
            "text": text,
        },
    ) as r:
        return r.json()


def send_new_order(ecommerce: str, order: Union[tiki.Order, None]) -> dict:
    return send_telegram(
        f"""Đơn hàng *{ecommerce}* mới
{divider}
```
{yaml.dump(order, allow_unicode=True)}
```
"""
    )


def send_created_order(ecommerce: str, id: str) -> dict:
    url = f"https://{os.getenv('ACCOUNT_ID')}\.app\.netsuite\.com/app/accounting/transactions/salesord\.nl?id\={id}"
    return send_telegram(
        f"""Tạo dơn hàng *{ecommerce}* thành công ^^
{divider}
Check ngay: [{url}]({url})
"""
    )


def send_error_create_order(ecommerce: str, error: Exception, order_ids: list[str]):
    return send_telegram(
        f"""Tạo đơn hàng *{ecommerce}* thất bại: {",".join(order_ids)}
{divider}
```
{repr(error)}
```
    """
    )
