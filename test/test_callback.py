import pytest

from controller.callback import callback_controller

def test_callback(update):
    res = callback_controller(update)
    res
