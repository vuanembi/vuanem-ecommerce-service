from typing import Any

from flask import Request
from returns.functions import raise_exception

from lazada import lazada_service, order_repo
from netsuite.order import order_service
from telegram import telegram


def lazada_controller(request: Request) -> dict[str, Any]:
    return (
        lazada_service.get_orders_service()
        .bind(
            order_service.ingest(
                order_repo.create,
                lazada_service.builder,
                telegram.LAZADA_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "lazada", "results": x})
        .lash(raise_exception)
        .unwrap()
    )
