import pytest

from libs.firestore import get_prepared_order
from libs.telegram import (
    send_created_order,
    send_create_order_error,
    send_closed_created_order,
)


@pytest.fixture()
def order():
    return "11111"


@pytest.fixture(params=["Tiki"])
def ecommerce(request):
    return request.param


def test_send_created_order(ecommerce, order):
    assert send_created_order(ecommerce, order)["ok"]


def test_send_error_create_order(ecommerce, order):
    assert send_create_order_error(ecommerce, Exception("Test exception"), order)["ok"]


def test_send_closed_created_order(ecommerce, order):
    assert send_closed_created_order(ecommerce, order)["ok"]


def test_get_prepared_order(callback_data):
    assert get_prepared_order(callback_data["v"])["order"]
