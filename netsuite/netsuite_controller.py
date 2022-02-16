from typing import Any, Optional

from flask import Request, abort
from returns.result import Success

from netsuite.analytics import analytics_service
from netsuite.order import order_service


analytics_services = {
    "/netsuite/analytics/coupon_code": analytics_service.coupon_code_analytics_service,
    "/netsuite/saved_search/coupon_code": analytics_service.coupon_code_ss_service,
}


def netsuite_controller(request: Request) -> dict[str, Any]:
    body: Optional[dict[str, Any]] = request.get_json()
    if body:
        if request.path in analytics_services:
            return analytics_services[request.path](body).unwrap()
        elif request.path == "/netsuite/restlet/sales_order":
            if request.method in ["POST", "PUT"] and "prepared_id" in body:
                svc = (
                    order_service.close
                    if request.method == "PUT"
                    else order_service.create
                )
                return (
                    svc(body["prepared_id"])  # type: ignore
                    .map(
                        lambda x: {
                            "status": 200,
                            "result": x[0],
                        }
                    )
                    .lash(lambda x: Success(abort(400, repr(x[0]))))
                ).unwrap()

            else:
                return abort(400)
        else:
            return abort(404)
    else:
        return abort(400)
