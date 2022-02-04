from typing import Any
import json

from flask import Request
from returns.result import Result, Success, Failure

from telegram import telegram, callback_service, message_service
from netsuite import netsuite_service


def service_factory(
    validated_update: tuple[str, int, telegram.CalbackData],
) -> Result[str, str]:
    chat_id, message_id, data = validated_update
    if data["t"] == "O":
        if data["a"] == 1:
            return (
                netsuite_service.create_order_service(data["v"])
                .map(
                    message_service.send_create_order_success(
                        chat_id,
                        message_id,
                        data["v"],
                    )
                )
                .alt(
                    message_service.send_create_order_error(
                        chat_id,
                        message_id,
                        data["v"],
                    )
                )
                .map(lambda x: str(x[0]))
                .lash(lambda x: Success(repr(x[0])))
            )
        elif data["a"] == -1:
            return (
                netsuite_service.close_order_service(data["v"])
                .map(message_service.send_close_order_success(chat_id, message_id))
                .alt(message_service.send_close_order_error(chat_id, message_id))
                .map(lambda x: str(x[0]))
                .lash(lambda x: Success(repr(x[0])))
            )
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request: Request) -> dict[str, Any]:
    return (
        callback_service.validation_service(request.get_json()) # type: ignore
        .bind(service_factory)
        .lash(lambda x: Success(x))
        .map(
            lambda x: {
                "controller": "callback",
                "detail": x,
            }
        )
        .unwrap()
    )
