import pytest

from controller.callback import handle_create_order, callback_controller

# def test_handle_create_order():


def test_callback(update):
    res = callback_controller(update)
    res
