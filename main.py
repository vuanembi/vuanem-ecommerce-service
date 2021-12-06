from controller.tiki import handle_event_queue
from controller.chatbot import handle_callback


def main(request) -> dict:
    request_json: dict = request.get_json()
    request_path: str = request.path

    print(request_path, request_json)

    if request_path == "/tiki":
        response = handle_event_queue()
    elif request_path == '/chatbot':
        response = handle_callback(request_json)

    print(response)
    return response
