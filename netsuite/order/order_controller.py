from typing import Any, Optional

from flask import Request, abort
from returns.functions import raise_exception

from netsuite.order import order, order_service

services = {
    "POST": order_service.create,
    "PUT": order_service.close,
}


def order_controller(request: Request) -> dict[str, Any]:
    body: Optional[order.OrderRequest] = request.get_json()
    if body and "id" in body:
        if request.method in services:
            return (
                services[request.method](body["id"])
                .map(lambda x: x.get(["order.id"]).to_dict()["order"]["id"])
                .map(lambda x: {"order_id": x})
                .lash(raise_exception)
            ).unwrap()

        else:
            return abort(405)
    else:
        return abort(400)
