import yaml

from netsuite.sales_order.sales_order_repo import get_url
from telegram import telegram, telegram_repo

DIVIDER = "\=\=\=\=\=\=\=\=\=\=\="


def send_new_order(channel: telegram.Channel):
    def _send(order: dict, id: str) -> tuple[dict, str]:
        telegram_repo.send(
            {
                "chat_id": channel.chat_id,
                "text": "\n".join(
                    [
                        f"Đơn hàng *{channel.ecom}* mới",
                        DIVIDER,
                        f"`{id}`",
                        DIVIDER,
                        "```",
                        yaml.dump(order, allow_unicode=True),
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
                                    id,
                                ),
                            },
                        ]
                    ],
                },
            }
        )
        return order, id

    return _send


def send_create_order_success(chat_id: str, message_id: int, id: str):
    def _send(res: tuple[int, str]) -> tuple[int, str]:
        _id, memo = res
        telegram_repo.send(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Tạo đơn hàng `{memo}` thành công^^",
                        DIVIDER,
                        f"Check ngay: [{get_url(str(_id))}]({get_url(str(_id))})",
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
                                    id,
                                ),
                            },
                        ]
                    ]
                },
            }
        )
        return res

    return _send


def send_create_order_error(chat_id: str, message_id: int):
    def _send(res: tuple[Exception, str]) -> tuple[Exception, str]:
        err, memo = res
        telegram_repo.send(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Tạo đơn hàng `{memo}` thất bại X\.X",
                        DIVIDER,
                        "```",
                        repr(err),
                        "```",
                    ]
                ),
            }
        )
        return res

    return _send


def send_close_order_success(chat_id: str, message_id: int):
    def _send(res: tuple[int, str]) -> tuple[int, str]:
        id, memo = res
        telegram_repo.send(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Đóng đơn hàng `{memo}` thành công `{id}`",
                        DIVIDER,
                        f"Check ngay: [{get_url(str(id))}]({get_url(str(id))})",
                    ]
                ),
            }
        )
        return res

    return _send


def send_close_order_error(chat_id: str, message_id: int):
    def _send(res: tuple[Exception, str, int]) -> tuple[Exception, str, int]:
        err, memo, id = res
        telegram_repo.send(
            {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "text": "\n".join(
                    [
                        f"Đóng đơn hàng `{memo}` thất bại `{id}`",
                        DIVIDER,
                        f"Check ngay: [{get_url(str(id))}]({get_url(str(id))})",
                        "```",
                        repr(err),
                        "```",
                    ]
                ),
            }
        )
        return res

    return _send
