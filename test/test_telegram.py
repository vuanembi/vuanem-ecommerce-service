import pytest

from libs.telegram import send_created_order, send_error_create_order


@pytest.fixture()
def order():
    return "11111"

@pytest.fixture(params=["Tiki"])
def ecommerce(request):
    return request.param

def test_send_created_order(ecommerce, order):
    res = send_created_order(ecommerce, order)
    assert res["ok"]

def test_send_error_create_order(ecommerce, order):
    res = send_error_create_order(ecommerce, Exception("Test exception"), [order])
    res
