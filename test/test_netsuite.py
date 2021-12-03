import requests
import pytest

from libs.netsuite import build_customer, get_customer_if_not_exist


@pytest.fixture()
def customer():
    return build_customer("HM", "2222222222")


def test_get_customer(customer):
    res = get_customer_if_not_exist(requests.Session(), customer)
    assert res
