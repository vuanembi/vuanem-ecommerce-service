from typing import Optional, Any
import os
import json

import yaml
from google.cloud.firestore import DocumentReference

from netsuite.order import order
from netsuite.sales_order import sales_order_repo
from telegram import telegram_repo
from common.utils import json_to_csv

DIVIDER = "\=\=\=\=\=\="


def safe_encode(value: Any) -> Optional[Any]:
    try:
        json.dumps(value)
        return value
    except:
        return None


def get_url(id_):
    return f"[{sales_order_repo.get_url(id_)}]({sales_order_repo.get_url(id_)})"


def get_chat_id(id_: str) -> str:
    return id_ if os.getenv("PYTHON_ENV") == "prod" else "-645664226"


def send_new_order(name: str, chat_id: str):
    def _send(order_ref: DocumentReference) -> DocumentReference:
        telegram_repo.sendMessage(
            {
                "chat_id": chat_id,
                "text": "\n".join(
                    [
                        f"Đơn hàng *{name}* mới",
                        DIVIDER,
                        "```",
                        yaml.dump(
                            {
                                k: safe_encode(v)
                                for k, v in order_ref.get(["source_ref"])
                                .get("source_ref")
                                .get()
                                .to_dict()
                                .items()
                            },
                            allow_unicode=True,
                        )[:4090],
                        "```",
                    ]
                ),
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Tạo đơn",
                                "callback_data": telegram_repo.build_callback_data(
                                    "O",
                                    1,
                                    order_ref.id,
                                ),
                            },
                        ]
                    ],
                },
            }
        )
        return order_ref

    return _send


def send_create_order_success(chat_id: str, message_id: int):
    def _send(order_ref: DocumentReference) -> DocumentReference:
        _order: order.Order = order_ref.get(["order.id", "order.memo"])
        telegram_repo.sendMessage(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Tạo đơn hàng `{_order.get('order.memo')}` thành công^^",
                        DIVIDER,
                        get_url(_order.get("order.id")),
                    ]
                ),
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Đóng đơn",
                                "callback_data": telegram_repo.build_callback_data(
                                    "O",
                                    -1,
                                    order_ref.id,
                                ),
                            },
                        ]
                    ]
                },
            }
        )
        return order_ref

    return _send


def send_create_order_error(chat_id: str, message_id: int):
    def _send(error: Exception) -> Exception:
        telegram_repo.sendMessage(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Tạo đơn hàng thất bại X\.X",
                        DIVIDER,
                        "```",
                        repr(error),
                        "```",
                    ]
                ),
            }
        )
        return error

    return _send


def send_close_order_success(chat_id: str, message_id: int):
    def _send(order_ref: DocumentReference) -> tuple[int, str]:
        _order = order_ref.get(["order.id", "order.memo"])
        telegram_repo.sendMessage(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Đóng đơn hàng `{_order.get('order.memo')}` thành công",
                        DIVIDER,
                        get_url(_order.get("order.id")),
                    ]
                ),
            }
        )
        return order_ref

    return _send


def send_close_order_error(chat_id: str, message_id: int):
    def _send(error: Exception) -> Exception:
        telegram_repo.sendMessage(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Đóng đơn hàng thất bại",
                        DIVIDER,
                        "```",
                        repr(error),
                        "```",
                    ]
                ),
            }
        )
        return error

    return _send


def send_products_alert(chat_id: str):
    def _send(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if products:
            telegram_repo.sendDocuments(
                {
                    "chat_id": chat_id,
                    "caption": "Có biến",
                    "disable_notification": True,
                },
                [("document", ("results.csv", json_to_csv(products), "text/csv"))],
            )
        else:
            telegram_repo.sendMessage({"chat_id": chat_id, "text": "Ko có biến"})  # type: ignore
        return products

    return _send
