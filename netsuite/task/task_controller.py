from flask import Request, abort

from netsuite.task.task_service import csv_import_service, bank_in_transit_service

services = {
    "/netsuite/task/csv_import": csv_import_service,
    "/netsuite/task/bank_in_transit": bank_in_transit_service,
}


def task_controller(request: Request):
    body = request.get_json()
    if request.path in services and body:
        return services[request.path](body).unwrap()
    else:
        abort(404)
