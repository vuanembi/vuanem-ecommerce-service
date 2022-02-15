from typing import Any

from flask import Request

from lazada import lazada_service, data_repo
from netsuite.sales_order import sales_order_service
from telegram import telegram


def lazada_controller(request: Request) -> dict[str, Any]:
    return (
        lazada_service.get_orders_service()
        .bind(
            sales_order_service.prepare_orders_service(
                data_repo.persist_order,
                lazada_service.prepared_order_builder,
                telegram.LAZADA_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "lazada", "results": x})
        .unwrap()
    )
