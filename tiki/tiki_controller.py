from flask import Request

from tiki import tiki_service

services = {
    "/tiki/orders/ingest": tiki_service.ingest_orders_service,
    "/tiki/products": tiki_service.get_products_service,
    "/tiki/products/alert": tiki_service.alert_products_service,
}


def tiki_controller(request: Request):
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
