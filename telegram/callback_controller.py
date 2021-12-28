from typing import Optional
import json

from returns.result import ResultE, Failure
from returns.pipeline import flow
from returns.pointfree import bind

from telegram import telegram, callback_service
from netsuite import netsuite_service


def service_factory(data: telegram.CalbackData) -> ResultE[Optional[str]]:
    if data["t"] == "O":
        if data["a"] == 1:
            return netsuite_service.create_order_service(data["v"])
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request_data: dict) -> dict:
    return flow(
        request_data,
        callback_service.validation_service(request_data),
        bind(service_factory),
        bind(
            lambda x: {
                "controller": "callback",
                "detail": x,
            }
        ),
    )
