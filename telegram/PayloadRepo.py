import json

import yaml

from netsuite.NetSuiteRepo import get_sales_order_url
from telegram.Telegram import Payload, CalbackData

DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def build_callback_data(type_: str, action: int, value: str) -> CalbackData:
    return json.dumps(
        {
            "t": type_,
            "a": action,
            "v": value,
        }
    )


def add_ack_callback() -> Payload:
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


def add_new_order(ecom: str, order: dict) -> Payload:
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


def add_new_order_callback(id: str) -> Payload:
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Tạo đơn",
                        "callback_data": build_callback_data("O", 1, id),
                    },
                ]
            ],
        }
    }


def add_create_order_success(id: str) -> Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{id}` thành công ^^",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    }


def add_create_order_error(error: Exception, id: str) -> Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{id}` thất bại X\.X",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    }


def add_create_order_callback(id: str) -> Payload:
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Đóng đơn",
                        "callback_data": build_callback_data("O", -1, id),
                    },
                ]
            ]
        }
    }


def add_close_order_success(id: str) -> Payload:
    return {
        "text": "\n".join(
            [
                f"Đóng đơn hàng `{id}` thành công X\.X",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    }
