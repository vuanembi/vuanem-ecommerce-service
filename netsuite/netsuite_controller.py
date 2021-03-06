from typing import Any

from flask import Request, abort

from netsuite.query.query_controller import query_controller
from netsuite.order.order_controller import order_controller
from netsuite.task.task_controller import task_controller


def netsuite_controller(request: Request) -> dict[str, Any]:
    if "analytics" in request.path or "saved_search" in request.path:
        return query_controller(request)
    elif "order" in request.path:
        return order_controller(request)
    elif "task" in request.path:
        return task_controller(request)
    else:
        abort(404)
