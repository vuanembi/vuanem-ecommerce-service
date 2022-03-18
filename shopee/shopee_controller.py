from flask import Request

from shopee import shopee_service

services = {
    "/shopee/orders/ingest": shopee_service.ingest_orders_service,
    "/shopee/items": shopee_service.get_items_service,
}


def shopee_controller(request: Request):
    if request.path in services:
        return (
            services[request.path]()
            .map(
                lambda x: {
                    "controller": request.path,
                    "results": x,
                }
            )
            .unwrap()
        )
