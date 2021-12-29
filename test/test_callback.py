from telegram import callback_controller, callback_service


def test_validation_service(telegram_update):
    res = callback_service.validation_service(telegram_update)
    res

def test_controller(telegram_update):
    res = callback_controller.callback_controller(telegram_update)
    res
