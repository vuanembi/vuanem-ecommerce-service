import pytest

from telegram import message_service


@pytest.fixture()
def order():
    return {"key": "value"}


@pytest.fixture(params=["Tiki"])
def ecommerce(request):
    return request.param


@pytest.fixture()
def id():
    return "11111"


def test_send_new_order(ecommerce, order, id):
    message_service.send_new_order(ecommerce, order, id)


def test_send_create_order_success(id):
    message_service.send_create_order_success(id)


def test_send_create_order_error():
    message_service.send_create_order_error(Exception("Test exception"))


# def test_send_closed_created_order(order):
#     assert send_closed_created_order(order)["ok"]
