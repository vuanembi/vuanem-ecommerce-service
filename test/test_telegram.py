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
    res = message_service.send_new_order(ecommerce, order, id)
    assert res


# def test_send_created_order(order):
#     assert send_created_order(order)["ok"]


# def test_send_error_create_order(order):
#     assert send_create_order_error(Exception("Test exception"), order)["ok"]


# def test_send_closed_created_order(order):
#     assert send_closed_created_order(order)["ok"]


# def test_get_prepared_order(callback_data):
#     assert get_prepared_order(callback_data["v"])["order"]
