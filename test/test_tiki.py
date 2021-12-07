import pytest

from test.utils import run
from controller.tiki import (
    add_customer,
    add_items,
    build_prepared_components,
    handle_orders,
)
from libs.tiki import get_order, pull_events
from libs.firestore import get_latest_ack_id
from libs.telegram import send_new_order


@pytest.fixture()
def order(session):
    return get_order(session, "678789503")


@pytest.fixture()
def prepared_customer():
    return {
        "entity": None,
        "custbody_customer_phone": "0938169869",
        "custbody_recipient_phone": "0938169869",
        "custbody_recipient": "Nguyễn Vũ Ngọc Giang",
        "shippingaddress": {"addressee": "Nguyễn Vũ Ngọc Giang"},
    }


@pytest.fixture()
def prepared_items():
    return {
        "items": [
            {
                "item": 196870,
                "quantity": 1,
                "price": -1,
                "amount": 5726363,
            },
        ],
    }


def test_pull_event(session):
    ack_id, events = pull_events(session, get_latest_ack_id())
    assert ack_id


def test_alert_on_order(order):
    res = send_new_order("TIKI", order)
    assert res


def test_add_customer(order, prepared_customer):
    assert add_customer(order) == prepared_customer


def test_add_items(order, prepared_items):
    assert add_items(order) == prepared_items


def test_build_prepared_components(order):
    res = build_prepared_components(order)
    assert res


def test_handle_orders(order):
    assert handle_orders([order])({})["orders"]


def test_tiki():
    res = run("/tiki")
    assert res["ack_id"]
