from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Result

from telegram import telegram, telegram_repo, callback_repo


def validation_service(
    update: telegram.Update,
) -> Result[tuple[str, int, telegram.CalbackData], str]:
    return flow(
        update,
        telegram_repo.answer_callback,
        callback_repo.validate_update,
        # bind(callback_repo.validate_callback),
        bind(callback_repo.validate_data),
    )
