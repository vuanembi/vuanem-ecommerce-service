from typing import Any

from flask import Request, abort
from returns.result import Result, ResultE
from returns.methods import cond

from netsuite.analytics import analytics_service

services = {
    "/netsuite/analytics/coupon_code": analytics_service.coupon_code_service,
}


def validation_service(
    request_data: dict[str, Any]
) -> Result[dict[str, Any], dict[str, Any]]:
    return cond(
        Result,
        "data" in request_data and isinstance(request_data["data"], list),
        request_data,
        request_data,
    )


def analytics_controller(request: Request) -> dict[str, Any]:
    body = request.get_json()
    if request.path in services and body:
        return services[request.path](body).unwrap()
    else:
        abort(404)
