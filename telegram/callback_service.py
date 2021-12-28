from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import ResultE
from returns.functions import tap

from telegram import telegram, telegram_repo, callback_repo


def validation_service(update: telegram.Update) -> ResultE[telegram.CalbackData]:
    return flow(
        update,
        tap(telegram_repo.answer_callback),
        callback_repo.validate_update,
        bind(callback_repo.validate_callback),
        bind(callback_repo.validate_data),
    )
