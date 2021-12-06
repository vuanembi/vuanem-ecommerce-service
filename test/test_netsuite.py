import requests
import pytest

from libs.netsuite import get_customer_if_not_exist
from models.netsuite.customer import build_customer_request


@pytest.fixture()
def customer():
    return build_customer_request("HM", "2222222222")


def test_get_customer(customer):
    res = get_customer_if_not_exist(requests.Session(), customer)
    assert res
