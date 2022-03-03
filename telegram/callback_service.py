from typing import Callable

from returns.pipeline import flow
from returns.pointfree import bind, map_, alt
from returns.result import Result, ResultE
from google.cloud.firestore import DocumentReference

from netsuite.order import order_service
from telegram import message_service, telegram, telegram_repo, callback_repo


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


def _operation(
    ops: Callable[[str], ResultE[DocumentReference]],
    msg_on_success: Callable[[str, int], DocumentReference],
    msg_on_failure: Callable[[str, int], DocumentReference],
):
    def __operation(
        chat_id: str,
        message_id: int,
        id: str,
    ) -> ResultE[DocumentReference]:
        return flow(
            id,
            ops,
            map_(msg_on_success(chat_id, message_id)),
            alt(msg_on_failure(chat_id, message_id)),
        )

    return __operation


create = _operation(
    order_service.create,
    message_service.send_create_order_success,
    message_service.send_create_order_error,
)

close = _operation(
    order_service.close,
    message_service.send_close_order_success,
    message_service.send_close_order_error,
)
