import requests
import pytest

from test.utils import run
from libs.tiki import get_order
from libs.telegram import send_tiki_order


@pytest.fixture()
def order():
    return get_order(requests.Session(), "753075217")

def test_send_telegram(order):
    res = send_tiki_order(order)
    assert res


def test_tiki():
    res = run("/tiki")
    assert res["results"]["ack_id"]
