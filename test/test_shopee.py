import pytest

from libs.shopee import get_order_details


@pytest.fixture()
def order():
    return "211101D83KXD9W"


def test_get_order_details(session, order):
    res = get_order_details(session, order)
    for item in res["items"]:
        assert item["variation_sku"]
