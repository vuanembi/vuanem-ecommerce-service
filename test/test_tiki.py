import pytest

from test.utils import run
from controller.tiki import (
    build_customer,
    build_items,
    build_prepared_order,
    handle_new_orders,
)
from libs.tiki import get_order, pull_events
from libs.firestore import get_latest_ack_id
from libs.telegram import send_new_order


@pytest.fixture()
def order(session):
    return get_order(session, "678789503")


def test_pull_event(session):
    ack_id, events = pull_events(session, get_latest_ack_id())
    assert ack_id


def test_alert_on_order(order):
    res = send_new_order("TIKI", order)
    assert res


def test_build_customer(oauth_session, order):
    res = build_customer(oauth_session, order)
    assert res


def test_build_items(oauth_session, order):
    res = build_items(oauth_session, order)
    assert res


def test_build_sales_order(order):
    res = build_prepared_order(order)
    assert res


def test_handle_new_sales_order(order):
    res = handle_new_orders([order])
    assert res["orders"]


def test_tiki():
    res = run("/tiki")
    assert res["ack_id"]
