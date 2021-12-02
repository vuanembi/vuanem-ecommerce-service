from controller.tiki import handle_event_queue


def main(request) -> dict:
    request_json: dict = request.get_json()
    request_path: str = request.path

    if request_path == "/tiki":
        response = handle_event_queue()

    print(response)
    return response
