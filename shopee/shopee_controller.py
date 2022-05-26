from flask import Request

from shopee import shopee_service, seller

sellers = {
    i.name: i
    for i in [
        seller.SHOPEE,
        seller.SHOPEE2,
    ]
}


def orders_controller(request: Request):
    return shopee_service.ingest_orders_service((request.get_json() or {})["seller"])


services = {
    "/shopee/orders/ingest": orders_controller,
    "/shopee/items": shopee_service.get_items_service,
}


def shopee_controller(request: Request):
    if request.path in services:
        return (
            services[request.path](request) # type: ignore
            .map(
                lambda x: {
                    "controller": request.path,
                    "results": x,
                }
            )
            .unwrap()
        )
