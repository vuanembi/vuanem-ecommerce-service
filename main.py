from controller.tiki import tiki_controller
from controller.callback import callback_controller


def main(request) -> dict:
    request_json: dict = request.get_json()
    request_path: str = request.path

    print(request_path, request_json)

    if request_path == "/tiki":
        response = tiki_controller()
    elif request_path == '/chatbot':
        response = callback_controller(request_json)

    print(response)
    return response
