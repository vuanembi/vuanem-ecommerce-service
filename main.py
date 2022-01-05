from typing import Callable, Any

from tiki.tiki_controller import tiki_controller
from lazada.lazada_controller import lazada_controller
from telegram.callback_controller import callback_controller
from netsuite.netsuite_controller import netsuite_controller

controllers: dict[str, Callable[[Any], dict]] = {
    "/tiki": tiki_controller,
    "/lazada": lazada_controller,
    "/callback": callback_controller,
    "/netsuite": netsuite_controller,
}


def main(request) -> dict:
    request_path: str = request.path

    print(request_path, request.get_json())

    if request_path.startswith("/tiki"):
        response = tiki_controller(request)
    elif request_path.startswith("/lazada"):
        response = lazada_controller(request)
    elif request_path.startswith("/callback"):
        response = callback_controller(request)
    elif request_path.startswith("/netsuite"):
        response = netsuite_controller(request)
    else:
        response = {
            "status": 200,
        }

    print(response)
    return response
