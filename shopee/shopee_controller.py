from flask import Request

from shopee import shopee_service, seller

services = {
    "/shopee/orders/ingest": shopee_service.ingest_orders_service,
    "/shopee/items": shopee_service.get_items_service,
}


def shopee_controller(request: Request):
    if request.path in services:
        _seller = seller.SELLERS[(request.get_json() or {})["seller"]]
        return (
            services[request.path](_seller)  # type: ignore
            .map(
                lambda x: {
                    "controller": request.path,
                    "seller": _seller.name,
                    "results": x,
                }
            )
            .unwrap()
        )
