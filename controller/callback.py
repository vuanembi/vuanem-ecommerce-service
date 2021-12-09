from libs.firestore import create_telegram_update, get_telegram_update
from libs.telegram import (
    get_callback_query_data,
    _send,
    answer_callback,
)
from libs.utils import compose
from models import telegram
from models.utils import Response, ResponseBuilder


def callback_controller(request_data: telegram.Update) -> Response:
    return compose(handle_echo(request_data), handle_update(request_data))(
        {
            "controller": "callback",
        }
    )


def handle_update(update: telegram.Update) -> ResponseBuilder:
    def handle(res: dict) -> Response:
        if get_telegram_update(update["update_id"]):
            return res
        else:
            return {
                **res,
                "update_id": create_telegram_update(update),
            }

    return handle


def handle_echo(update: telegram.Update) -> ResponseBuilder:
    def handle(res: dict) -> Response:
        if res.get("update_id"):
            callback_query_id, data_str = get_callback_query_data(update)
            answer_callback(callback_query_id)
            _send({"text": f"`{data_str}`"})
            return {
                **res,
                "data_str": data_str,
            }
        else:
            return res

    return handle
