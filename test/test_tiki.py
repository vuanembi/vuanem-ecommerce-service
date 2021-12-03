import requests
import pytest

from test.utils import run
from controller.tiki import build_customer, build_items, build_sales_order, handle_new_orders
from libs.tiki import get_order
from libs.netsuite import create_sales_order
from libs.restlet import netsuite_session
from libs.telegram import send_new_order


@pytest.fixture()
def session():
    return requests.Session()


@pytest.fixture()
def oauth_session():
    return netsuite_session()


@pytest.fixture()
def order(session):
    return get_order(session, "753075217")


def test_alert_on_order(order):
    res = send_new_order('TIKI', order)
    assert res


def test_build_customer(oauth_session, order):
    res = build_customer(oauth_session, order)
    assert res


def test_build_items(oauth_session, order):
    res = build_items(oauth_session, order)
    assert res


def test_build_sales_order(oauth_session, order):
    res = build_sales_order(oauth_session, order)
    assert res


def test_create_sales_order(oauth_session, order):
    res = create_sales_order(
        oauth_session,
        build_sales_order(oauth_session, order),
    )
    assert res

def test_handle_new_sales_order(order):
    res = handle_new_orders([order])
    assert res['orders']


def test_tiki():
    res = run("/tiki")
    assert res["ack_id"]
