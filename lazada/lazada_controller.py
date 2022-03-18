from flask import Request

from lazada import lazada_service

services = {
    "/lazada/orders/ingest": lazada_service.ingets_orders_service,
    "/lazada/products": lazada_service.get_products_service,
}


def lazada_controller(request: Request):
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
