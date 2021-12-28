import pytest

from telegram import callback_service


def test_validation_service(telegram_update):
    res = callback_service.validation_service(telegram_update)
    res
