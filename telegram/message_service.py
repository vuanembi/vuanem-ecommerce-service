from common.utils import compose
from telegram import telegram, telegram_repo, payload_repo

# ----------------------------------- Send ----------------------------------- #


def send_new_order(channel: telegram.Channel):
    def _send(order: dict, id: int) -> tuple[dict, int]:
        telegram_repo.send(
            channel,
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_new_order,
                    channel.ecom,
                    order,
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_new_order_callback,
                    id,
                ),
            ),
        )
        return order, id

    return _send


def send_create_order_success(chat_id: str, message_id: int):
    def _send(res: tuple[int, str]) -> tuple[int, str]:
        id, memo = res
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_create_order_success,
                    id,
                    memo,
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_create_order_callback,
                    id,
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_message_reply,
                    message_id,
                ),
            ),
        )
        return res

    return _send


def send_create_order_error(chat_id: str, message_id: int):
    def _send(res: tuple[Exception, str]) -> tuple[Exception, str]:
        err, memo = res
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_create_order_error,
                    err,
                    memo,
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_message_reply,
                    message_id,
                ),
            ),
        )
        return res

    return _send


def send_close_order_success(chat_id: str, message_id: int):
    def _send(res: tuple[Exception, str]) -> tuple[Exception, str]:
        id, memo = res
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_close_order_success,
                    id,
                    memo,
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_message_reply,
                    message_id,
                ),
            ),
        )
        return res

    return _send


def send_close_order_error(chat_id: str, message_id: int):
    def _send(res: tuple[Exception, str, int]) -> tuple[Exception, str, int]:
        err, memo, transaction_id = res
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_close_order_error,
                    err,
                    memo,
                    str(transaction_id),
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_message_reply,
                    message_id,
                ),
            ),
        )
        return res

    return _send
