import pytest

from libs.telegram import send_created_order


@pytest.fixture()
def order():
    return "11111"


@pytest.mark.parametrize("ecommerce", ["Tiki"])
def test_send_created_order(ecommerce, order):
    res = send_created_order(ecommerce, order)
    assert res["ok"]
