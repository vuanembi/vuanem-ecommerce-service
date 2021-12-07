import json

from libs.telegram import (
    is_chat_id,
    is_callback,
    get_callback_query_data,
    _send_telegram,
    answer_callback,
)
from models import telegram


def callback_controller(request_data: telegram.Update) -> dict:
    if is_chat_id(request_data) and is_callback(request_data):
        callback_query_id, data = get_callback_query_data(request_data)
        print(data)
        answer_callback(callback_query_id)
        _send_telegram({"text": f"`{json.dumps(data)}`"})
    return {
        "controller": "callback",
    }
