from lazada import lazada_service, data_repo
from netsuite import netsuite_service
from telegram import telegram


def lazada_controller(request) -> dict:
    return (
        lazada_service.get_orders_service()
        .bind(
            netsuite_service.prepare_orders_service(
                data_repo.persist_order,
                lazada_service.prepared_order_builder,
                telegram.LAZADA_CHANNEL,
            )
        )
        .map(lambda x: {"controller": "lazada", "results": x})
        .unwrap()
    )
