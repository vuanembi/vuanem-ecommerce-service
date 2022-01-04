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


def send_create_order_success(chat_id: str):
    def _send(id: str) -> str:
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_create_order_success,
                    id,
                ),
                telegram_repo.build_send_payload(payload_repo.add_ack_callback),
            ),
        )
        return id

    return _send


def send_create_order_error(chat_id: str):
    def _send(err: str) -> str:
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_create_order_error,
                    err,
                ),
                telegram_repo.build_send_payload(payload_repo.add_ack_callback),
            ),
        )
        return err

    return _send


def send_close_order(chat_id: str):
    def _send(id: str) -> str:
        telegram_repo.send(
            telegram.Channel("", chat_id),
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_close_order_success,
                    id,
                ),
                telegram_repo.build_send_payload(payload_repo.add_ack_callback),
            ),
        )
        return id

    return _send
