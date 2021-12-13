from returns.pipeline import flow
from returns.pointfree import bind, bind_optional
from returns.maybe import Maybe, Some, Nothing
from returns.io import IOResultE

import requests

from libs.shopee import get_order_details
from models.ecommerce import shopee

def shopee_controller(request_data: shopee.OrderStatusPush) -> dict:
    x: shopee.Order = flow(
        request_data,
        unpaid_status_predicate,
        bind_optional(get_push_order_id),
        bind_optional(get_push_order),
    )
    return {}

def unpaid_status_predicate(push: shopee.OrderStatusPush) -> Maybe[shopee.OrderStatusPush]:
    return Some(push) if push['data']['status'] == 'UNPAID' else Nothing

def get_push_order_id(push: shopee.OrderStatusPush) -> str:
    return push['data']['ordersn']

def get_push_order(ordersn: str) -> shopee.Order:
    with requests.Session() as session:
        return get_order_details(session, ordersn)
