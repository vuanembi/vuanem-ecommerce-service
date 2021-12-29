from returns.curry import curry

from common.utils import compose
from telegram import telegram_repo, payload_repo

# ----------------------------------- Send ----------------------------------- #


def send_new_order(ecom: str):
    @curry
    def _send(order: dict, id: str):
        telegram_repo.send(
            compose(
                telegram_repo.build_send_payload(
                    payload_repo.add_new_order, ecom, order
                ),
                telegram_repo.build_send_payload(
                    payload_repo.add_new_order_callback, id
                ),
            )
        )
        return order, id

    return _send


def send_create_order_success(id: str) -> None:
    # ! todo: close order callback
    telegram_repo.send(
        compose(
            telegram_repo.build_send_payload(payload_repo.add_create_order_success, id),
            telegram_repo.build_send_payload(payload_repo.add_ack_callback),
        )
    )


def send_create_order_error(error: Exception) -> None:
    telegram_repo.send(
        compose(
            telegram_repo.build_send_payload(
                payload_repo.add_create_order_error, error
            ),
            telegram_repo.build_send_payload(payload_repo.add_ack_callback),
        )
    )


def send_close_order(id: str) -> None:
    telegram_repo.send(
        compose(
            telegram_repo.build_send_payload(payload_repo.add_close_order_success, id),
            telegram_repo.build_send_payload(payload_repo.add_ack_callback),
        )
    )
