import json

import yaml

from netsuite.sales_order.sales_order_repo import get_url
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


def add_message_reply(message_id: int) -> telegram.Payload:
    return {
        "reply_to_message_id": message_id,
    }


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


def add_new_order(ecom: str, order: dict, prepared_id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đơn hàng *{ecom}* mới",
                DIVIDER,
                f"`{prepared_id}`",
                DIVIDER,
                "```",
                yaml.dump(order, allow_unicode=True),
                "```",
            ]
        )
    }


def add_new_order_callback(prepared_id: str) -> telegram.Payload:
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Tạo đơn",
                        "callback_data": build_callback_data("O", 1, prepared_id),
                    },
                ]
            ],
        },
    }


def add_create_order_success(id: str, memo: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{memo}` thành công `{id}` ^^",
                DIVIDER,
                f"Check ngay: [{get_url(id)}]({get_url(id)})",
            ]
        )
    }


def add_create_order_error(error: Exception, memo: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Tạo đơn hàng `{memo}` thất bại X\.X",
                DIVIDER,
                "```",
                repr(error),
                "```",
            ]
        )
    }


def add_create_order_callback(prepared_id: str) -> telegram.Payload:
    return {
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Đóng đơn",
                        "callback_data": build_callback_data("O", -1, prepared_id),
                    },
                ]
            ]
        }
    }


def add_close_order_success(id: str, memo: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đóng đơn hàng `{memo}` thành công `{id}`",
                DIVIDER,
                f"Check ngay: [{get_url(id)}]({get_url(id)})",
            ]
        )
    }


def add_close_order_error(error: Exception, memo: str, id: str) -> telegram.Payload:
    return {
        "text": "\n".join(
            [
                f"Đóng đơn hàng `{memo}` thất bại `{id}`",
                DIVIDER,
                f"Check ngay: [{get_url(id)}]({get_url(id)})",
                "```",
                repr(error),
                "```",
            ]
        )
    }
