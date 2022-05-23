from flask import Request, abort

from netsuite.task import task_service

services = {
    "/netsuite/task/csv_import": task_service.csv_import_service,
    "/netsuite/task/bank_in_transit": task_service.bank_in_transit_service,
    "/netsuite/task/voucher_adjustments": task_service.voucher_adjustments_service,
}


def task_controller(request: Request):
    body = request.get_json()
    if request.path in services and body:
        return services[request.path](body).unwrap()
    else:
        abort(404)
