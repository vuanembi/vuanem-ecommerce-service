import json

import yaml

from netsuite.netsuite_repo import get_sales_order_url
from telegram import telegram

DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def build_callback_data(type_: str, action: int, value: str) -> str:
    return json.dumps(
        {
            "t": type_,
            "a": action,
            "v": value,
        }
    )


def add_ack_callback() -> telegram.Payload:
    return {
        "reply_markup": {
            "keyboard": [
                [
                    {
                        "text": "Đã nhận thông tin",
                    },
                ],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    }


def add_new_order(ecom: str, order: dict) -> telegram.Payload:
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


def add_new_order_callback(id: str) -> telegram.Payload:
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
        },
    }


def add_create_order_success(id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{id}` thành công ^^",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    }


def add_create_order_error(error: Exception) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng thất bại X\.X",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    }


def add_create_order_callback(id: str) -> telegram.Payload:
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


def add_close_order_success(id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đóng đơn hàng `{id}` thành công X\.X",
                DIVIDER,
                f"Check ngay: [{get_sales_order_url(id)}]({get_sales_order_url(id)})",
            ]
        )
    }
