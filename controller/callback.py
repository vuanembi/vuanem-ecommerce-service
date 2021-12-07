from libs.telegram import get_callback_query_data
from models import telegram


def callback_controller(request_data: telegram.Update) -> dict:
    data = get_callback_query_data(request_data)
    print(data)
    return {}
