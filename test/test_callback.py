from telegram import callback_service

from test.conftest import run


def test_validation_service(telegram_update):
    res = callback_service.validation_service(telegram_update)
    res


def test_controller(telegram_update):
    res = run("/callback", telegram_update)
    res
