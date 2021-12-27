from tiki.tiki_controller import tiki_controller
# from controller.callback import callback_controller

controllers = {
    "/tiki": tiki_controller,
    # "/callback": callback_controller,
}


def main(request) -> dict:
    request_json: dict = request.get_json()
    request_path: str = request.path

    print(request_path, request_json)

    if request_path in controllers:
        response = controllers[request_path](request_json)
    else:
        response = {
            "status": 200,
        }
    print(response)
    return response
