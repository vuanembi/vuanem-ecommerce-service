from typing import Any

from flask import Request

from shopee import shopee_service, data_repo
from netsuite.sales_order import sales_order_service
from telegram import telegram


def shopee_controller(request: Request) -> dict[str, Any]:
    return (
        shopee_service.get_orders_service()
        .bind(
            sales_order_service.prepare_orders_service(
                data_repo.persist_order,  # type: ignore
                shopee_service.prepared_order_builder,
                telegram.SHOPEE_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "shopee", "results": x})
        .unwrap()
    )
