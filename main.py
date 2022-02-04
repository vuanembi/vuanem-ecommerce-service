from typing import Any

from flask import Request, abort

from tiki.tiki_controller import tiki_controller
from lazada.lazada_controller import lazada_controller
from shopee.shopee_controller import shopee_controller
from telegram.callback_controller import callback_controller
from netsuite.netsuite_controller import netsuite_controller


def main(request: Request) -> dict[str, Any]:
    request_path = request.path

    print(request_path, request.get_json())

    if request_path.startswith("/tiki"):
        response = tiki_controller(request)

    elif request_path.startswith("/lazada"):
        response = lazada_controller(request)

    elif request_path.startswith("/shopee"):
        response = shopee_controller(request)

    elif request_path.startswith("/callback"):
        response = callback_controller(request)

    elif request_path.startswith("/netsuite"):
        response = netsuite_controller(request)

    else:
        response = abort(404)

    print(response)
    return response
