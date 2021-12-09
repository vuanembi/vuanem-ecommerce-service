import pytest

from libs.firestore import (
    create_tiki_ack_id,
    get_latest_tiki_ack_id,
    create_prepared_order,
    create_telegram_update,
    get_telegram_update,
)


@pytest.fixture()
def ack_id():
    return "11111"


def test_create_tiki_ack_id(ack_id):
    assert create_tiki_ack_id(ack_id) == ack_id


def test_get_latest_tiki_ack_id():
    res = get_latest_tiki_ack_id()
    res.id


def test_create_telegram_update(update):
    assert create_telegram_update(update) == str(update["update_id"])


def test_get_telegram_update(update):
    assert (
        get_telegram_update(update["update_id"])["update"]["update_id"]
        == update["update_id"]
    )


def test_create_prepared_order(prepared_order):
    res = create_prepared_order(prepared_order)
    res
