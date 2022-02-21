from typing import Any, Optional

from flask import Request, abort
from returns.result import Success

from netsuite.query import query_controller
from netsuite.journal_entry import journal_entry_controller
from netsuite.order import order_service


query_path = [
    "analytics",
    "saved_search",
]


def netsuite_controller(request: Request) -> dict[str, Any]:
    body: Optional[dict[str, Any]] = request.get_json()
    for path in query_path:
        if path in request.path:
            return query_controller.query_controller(request)
    if "journal_entry" in request.path :
        return journal_entry_controller.journal_entry_controller(request)
    if request.path == "/netsuite/order" and body:
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
