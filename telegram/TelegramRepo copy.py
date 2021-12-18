from typing import Callable, Optional
import os
import json

import yaml
import requests

from common.utils import compose
from netsuite.NetSuiteRepo import get_sales_order_url
from models import telegram
from models.ecommerce import ecommerce

BASE_URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"
CHAT_ID = "-1001685563275" if os.getenv("PYTHON_ENV") == "prod" else "-645664226"
DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def get_callback_query(update: telegram.Update) -> tuple[str, Optional[dict]]:
    return (
        update["callback_query"]["id"],
        get_callback_query_data(update),
    )


def get_callback_query_data(update: telegram.Update) -> Optional[dict]:
    try:
        return json.loads(update["callback_query"].get("data"))
    except (TypeError, json.decoder.JSONDecodeError):
        return None


def _build_send_payload(builder: Callable, *args) -> telegram.PayloadBuilder:
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


def _send(payload_composer: telegram.PayloadBuilder) -> dict:
    with requests.post(
        f"{BASE_URL}/sendMessage",
        json=payload_composer(
            {
                "chat_id": CHAT_ID,
                "parse_mode": "MarkdownV2",
            }
        ),
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
                        "text": "Tạo đơn",
                        "callback_data": build_callback_data("O", 1, prepared_order_id),
                    },
                ]
            ],
        }
    }


def _add_acknowledge_callback() -> telegram.Payload:
    return {
        "reply_markup": {
            "keyboard": [
                [
                    {
                        "text": "Đã Nhận thông tin",
                    },
                ],
            ]
        }
    }


def _add_created_order(prepared_order_id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{prepared_order_id}` thành công ^^",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(prepared_order_id)}]({get_sales_order_url(prepared_order_id)})",
            ]
        )
    }


def _add_create_order_error(
    error: Exception,
    prepared_order_id: str,
) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{prepared_order_id}` thất bại X\.X",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    }


def _add_closed_created_order(prepared_order_id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đóng đơn hàng `{prepared_order_id}` thành công X\.X",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(prepared_order_id)}]({get_sales_order_url(prepared_order_id)})",
            ]
        )
    }


def _add_closed_created_order_callback(prepared_order_id: str) -> telegram.Payload:
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Đóng đơn",
                        "callback_data": build_callback_data(
                            "O", -1, prepared_order_id
                        ),
                    },
                ]
            ]
        }
    }


def send_new_order(ecom: str, order: ecommerce.Order, prepared_order_id: str) -> dict:
    return _send(
        compose(
            _build_send_payload(_add_new_ecommerce_order, ecom, order),
            _build_send_payload(_add_new_ecommerce_order_callback, prepared_order_id),
        )
    )


def send_created_order(id: str) -> dict:
    # ! todo: close order callback
    return _send(
        compose(
            _build_send_payload(_add_created_order, id),
            # _build_send_payload(_add_closed_created_order_callback, id),
            _build_send_payload(_add_acknowledge_callback),
        )
    )


def send_create_order_error(error: Exception, id: str) -> dict:
    return _send(
        compose(
            _build_send_payload(_add_create_order_error, error, id),
            _build_send_payload(_add_acknowledge_callback),
        )
    )


def send_closed_created_order(id: str) -> dict:
    return _send(
        compose(
            _build_send_payload(_add_closed_created_order, id),
            _build_send_payload(_add_acknowledge_callback),
        )
    )
