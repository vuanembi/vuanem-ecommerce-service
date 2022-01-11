import json

from returns.result import Result, Success, Failure

from telegram import telegram, callback_service
from netsuite import netsuite_service


def service_factory(
    validated_update: tuple[str, int, telegram.CalbackData],
) -> Result[str, str]:
    chat_id, message_id, data = validated_update
    if data["t"] == "O":
        if data["a"] == 1:
            return (
                netsuite_service.create_order_service(
                    chat_id,
                    message_id,
                    data["v"],
                )
                .map(lambda x: str(x[0]))
                .lash(lambda x: Success(repr(x[0])))
            )
        elif data["a"] == -1:
            return (
                netsuite_service.close_order_service(
                    chat_id,
                    message_id,
                    data["v"],
                )
                .map(lambda x: str(x[0]))
                .lash(lambda x: Success(repr(x[0])))
            )
    return Failure(f"Operation not supported {json.dumps(data)}")


def callback_controller(request) -> dict:
    return (
        callback_service.validation_service(request.get_json())
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
