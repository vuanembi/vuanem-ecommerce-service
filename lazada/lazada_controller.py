from flask import Request

from lazada import lazada_service, seller


services = {
    "/lazada/orders/ingest": lazada_service.ingest_orders_service,
    "/lazada/products": lazada_service.get_products_service,
}


def lazada_controller(request: Request):
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
