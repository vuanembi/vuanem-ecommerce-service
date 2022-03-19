from typing import Any

from flask import Request, abort

from netsuite.csv_import.csv_import_service import csv_import_service

services = {
    "/netsuite/task/csv_import": csv_import_service
}


def csv_import_controller(request: Request):
    body = request.get_json()
    if request.path in services and body:
        return services[request.path](body).unwrap()
    else:
        abort(404)
