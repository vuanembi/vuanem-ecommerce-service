from typing import Any
import json

from flask import Request
from returns.result import Result, Success, Failure

from telegram import telegram, callback_service

service = {
    "O": {
        1: callback_service.create,
        -1: callback_service.close,
    }
}


def service_factory(
    validated_update: tuple[str, int, telegram.CalbackData],
) -> Result[str, str]:
    chat_id, message_id, data = validated_update
    if data["t"] in service and data["a"] in service[data["t"]]:
        return service[data["t"]][data["a"]](chat_id, message_id, data["v"])
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request: Request) -> dict[str, Any]:
    return (
        callback_service.validation_service(request.get_json())  # type: ignore
        .bind(service_factory)
        .lash(lambda x: Success(x))
        .map(
            lambda x: {
                "controller": "callback",
                "result": x,
            }
        )
        .unwrap()
    )
