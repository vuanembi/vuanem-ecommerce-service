from common.utils import compose

from telegram.TelegramRepo import build_send_payload, send
from telegram.PayloadRepo import (
    add_new_ecommerce_order,
    add_new_ecommerce_order_callback,
    add_ack_callback,
    add_create_order_success,
    add_create_order_error,
    add_close_order,
)

# ----------------------------------- Send ----------------------------------- #


def send_new_order(ecom: str, order: dict, id: str) -> dict:
    return send(
        compose(
            build_send_payload(add_new_ecommerce_order, ecom, order),
            build_send_payload(add_new_ecommerce_order_callback, id),
        )
    )


def send_create_order_success(id: str) -> dict:
    # ! todo: close order callback
    return send(
        compose(
            build_send_payload(add_create_order_success, id),
            build_send_payload(add_ack_callback),
        )
    )


def send_create_order_error(error: Exception, id: str) -> dict:
    return send(
        compose(
            build_send_payload(add_create_order_error, error, id),
            build_send_payload(add_ack_callback),
        )
    )


def send_close_order(id: str) -> dict:
    return send(
        compose(
            build_send_payload(add_close_order, id),
            build_send_payload(add_ack_callback),
        )
    )
