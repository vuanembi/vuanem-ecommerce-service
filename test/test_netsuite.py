import requests
import pytest

from libs.netsuite import (
    get_customer_if_not_exist,
    build_customer_request,
    build_sales_order_from_prepared,
)


@pytest.fixture()
def customer():
    return build_customer_request("HM", "2222222222")


def test_get_customer(customer):
    res = get_customer_if_not_exist(requests.Session(), customer)
    assert res


def test_build_sales_order_from_prepared(oauth_session, prepared_order, netsuite_order):
    assert build_sales_order_from_prepared(oauth_session, prepared_order)  == netsuite_order
