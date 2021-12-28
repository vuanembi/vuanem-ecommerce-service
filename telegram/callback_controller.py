import json

from returns.result import Failure

from telegram import telegram, callback_service
from netsuite import netsuite_service


def service_factory(data: telegram.CalbackData):
    if data["t"] == "O":
        if data["a"] == 1:
            return netsuite_service.create_order_service(data["v"])
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request_data: dict):
    flow = callback_service.validation_service(request_data)
