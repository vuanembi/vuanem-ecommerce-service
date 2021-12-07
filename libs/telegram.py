from typing import Callable, Optional
import os
import json

import yaml
import requests

from libs.utils import compose
from libs.netsuite import get_sales_order_url
from models import telegram
from models.ecommerce import ecommerce


CHAT_ID = os.getenv("CHAT_ID")
DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def _get_chat_id(update: telegram.Update) -> Optional[int]:
    return update.get("callback_query", {}).get("message", {}).get("chat", {}).get("id")


def _filter_chat_id(update: telegram.Update) -> bool:
    return True if str(_get_chat_id(update)) == CHAT_ID else False


def get_callback_query_data(update: telegram.Update) -> dict:
    return (
        json.loads(update["callback_query"].get("data"))
        if _filter_chat_id(update)
        else None
    )


def _build_send_payload(builder: Callable, *args):
    def build(payload: telegram.Payload) -> telegram.Payload:
        return {
            **payload,
            **builder(*args),
        }

    return build


def build_callback_data(type_: str, action: int, value: str) -> telegram.CalbackData:
    return json.dumps(
        {
            "t": type_,
            "a": action,
            "v": value,
        }
    )


def _send_telegram(payload: telegram.Payload) -> dict:
    with requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json={
            **payload,
            "chat_id": CHAT_ID,
            "parse_mode": "MarkdownV2",
        },
    ) as r:
        r.raise_for_status()
        return r.json()


def _add_new_ecommerce_order(ecom: str, order: ecommerce.Order) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đơn hàng *{ecom}* mới",
                DIVIDER,
                "```",
                yaml.dump(order, allow_unicode=True),
                "```",
            ]
        )
    }


def _add_new_ecommerce_order_callback(prepared_order_id: str):
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Tạo đơn (+)",
                        "callback_data": build_callback_data("O", 1, prepared_order_id),
                    },
                    {
                        "text": "Huỷ đơn (-)",
                        "callback_data": build_callback_data(
                            "O", -1, prepared_order_id
                        ),
                    },
                ]
            ]
        }
    }


def _add_acknowledge_callback():
    return {
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
        }
    }


def _add_created_order(ecom: str, id: str) -> dict:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng *{ecom}* thành công ^^",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    }


def _add_create_order_error(ecom: str, error: Exception, id: str):
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng *{ecom}* thất bại: `{id}`",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    }


def send_new_order(ecom: str, order: ecommerce.Order, prepared_order_id: str) -> dict:
    return _send_telegram(
        compose(
            _build_send_payload(_add_new_ecommerce_order, ecom, order),
            _build_send_payload(_add_new_ecommerce_order_callback, prepared_order_id),
        )({})
    )


def send_created_order(ecom: str, id: str):
    return _send_telegram(
        compose(
            _build_send_payload(_add_created_order, ecom, id),
            _build_send_payload(_add_acknowledge_callback),
        )({})
    )


def send_create_order_error(ecom: str, error: Exception, id: str):
    return _send_telegram(
        compose(
            _build_send_payload(_add_create_order_error, ecom, error, id),
            _build_send_payload(_add_acknowledge_callback),
        )({})
    )
