from typing import Any, Optional

from flask import Request, abort
from returns.result import Success

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
                services[request.method](body["id"])  # type: ignore
                .map(
                    lambda x: {
                        "status": 200,
                        "result": x[0],
                    }
                )
                .lash(lambda x: Success(abort(400, repr(x[0]))))
            ).unwrap()

        else:
            return abort(405)
    else:
        return abort(400)
