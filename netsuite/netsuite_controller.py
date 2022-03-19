from typing import Any

from flask import Request, abort

from netsuite.query.query_controller import query_controller
from netsuite.journal_entry.journal_entry_controller import journal_entry_controller
from netsuite.order.order_controller import order_controller
from netsuite.csv_import.csv_import_controller import csv_import_controller


def netsuite_controller(request: Request) -> dict[str, Any]:
    if "analytics" in request.path or "saved_search" in request.path:
        return query_controller(request)
    elif "order" in request.path:
        return order_controller(request)
    elif "journal_entry" in request.path:
        return journal_entry_controller(request)
    elif "task" in request.path:
        return csv_import_controller(request)
    else:
        abort(404)
