from datetime import datetime

from returns.result import Result, Success
from returns.maybe import Some
from returns.pipeline import flow
from returns.pointfree import apply

from lazada import lazada_service, data_repo

def lazada_controller(request_data: dict):
    x = lazada_service.get_order_service()
    x
