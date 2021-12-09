import pytest

from controller.callback import callback_controller

def test_callback(update):
    assert callback_controller(update)["ok"]
