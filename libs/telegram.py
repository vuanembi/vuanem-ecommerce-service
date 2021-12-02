import os

import yaml
import requests

from libs.tiki import Order


def send_telegram(text: str) -> bool:
    with requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json={
            "chat_id": "-1001685563275",
            "parse_mode": "MarkdownV2",
            "text": text,
        },
    ) as r:
        return r.json()["ok"]


def send_tiki_order(order: Order) -> bool:
    return send_telegram(
        f"""Đơn hàng *Tiki* mới
\=\=\=\=\=\=\=\=\=\=\=
```
{yaml.dump(order, allow_unicode=True)}
```
"""
    )
