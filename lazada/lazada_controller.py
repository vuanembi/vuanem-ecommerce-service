from flask import Request

from lazada import lazada_service, seller

sellers = {
    i.name: i
    for i in [
        seller.LAZADA,
        seller.LAZADA2,
    ]
}


def orders_controller(request: Request):
    return lazada_service.ingest_orders_service(sellers[request.get_json()["seller"]])


services = {
    "/lazada/orders/ingest": orders_controller,
    "/lazada/products": lazada_service.get_products_service,
}


def lazada_controller(request: Request):
    if request.path in services:
        return (
            services[request.path](request)
            .map(
                lambda x: {
                    "controller": request.path,
                    "results": x,
                }
            )
            .unwrap()
        )
