from typing import Union
import os

import yaml
import requests

from libs import tiki

divider = "\=\=\=\=\=\=\=\=\=\=\="


def send_telegram(text: str) -> dict:
    with requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json={
            "chat_id": "-1001685563275",
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
        f"""Ôi bạn ơi, Tạo Đơn hàng *{ecommerce}* thành công ^^
{divider}
Xem ngay: [{url}]({url})
"""
    )
