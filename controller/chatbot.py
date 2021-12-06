from libs.telegram import get_callback_query_data, send_telegram
from models import telegram

def handle_callback(request_data: telegram.Update) -> dict:
    data = get_callback_query_data(request_data)
    print(data)
    return send_telegram("nhận thông tin")
