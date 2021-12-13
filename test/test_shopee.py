import pytest

from controller.shopee import shopee_controller
from libs.shopee import get_order_details

@pytest.fixture()
def order():
    return "211101D83KXD9W"
    
@pytest.fixture()
def push(order):
    return {
    "data": {
        "items": [],
        "ordersn": order,
        "status": "UNPAID",
    },
    "shop_id": 29042,
    "code": 3,
}




def test_get_order_details(session, order):
    res = get_order_details(session, order)
    for item in res["items"]:
        assert item["variation_sku"]

def test_controller(push):
    res = shopee_controller(push)
    res
