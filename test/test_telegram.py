import pytest

from telegram import telegram, message_service

channels = [
    telegram.TIKI_CHANNEL,
]


@pytest.fixture()
def order():
    return {"key": "value"}


@pytest.fixture(
    params=channels,
    ids=[i.ecom for i in channels],
)
def channel(request):
    return request.param


@pytest.fixture()
def id():
    return "test"


def test_send_new_order(channel, order, id):
    message_service.send_new_order(channel)(order)(id)


def test_send_create_order_success(id):
    message_service.send_create_order_success(id)


def test_send_create_order_error():
    message_service.send_create_order_error(Exception("Test exception"))


# def test_send_closed_created_order(order):
#     assert send_closed_created_order(order)["ok"]
