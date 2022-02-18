from typing import Any

from flask import Request

from shopee import shopee_service, order_repo
from netsuite.order import order_service
from telegram import telegram


def shopee_controller(request: Request) -> dict[str, Any]:
    return (
        shopee_service.get_orders_service()
        .bind(
            order_service.ingest(
                order_repo.create,  # type: ignore
                shopee_service.builder,
                telegram.SHOPEE_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "shopee", "results": x})
        .unwrap()
    )
