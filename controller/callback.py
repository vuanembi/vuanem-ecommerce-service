import json

from libs.restlet import netsuite_session
from libs.netsuite import create_sales_order, build_sales_order_from_prepared
from libs.firestore import (
    create_telegram_update,
    get_telegram_update,
    get_prepared_order,
    update_prepared_order_created,
)
from libs.telegram import (
    get_callback_query,
    _send,
    answer_callback,
    send_created_order,
    send_create_order_error,
)
from libs.utils import compose
from models import telegram
from models.utils import Response, ResponseBuilder


def callback_controller(request_data: telegram.Update) -> Response:
    return compose(
        handle_cleanup,
        handle_create_order,
        handle_prepared_order,
        handle_echo(request_data),
        handle_update(request_data),
    )(
        {
            "controller": "callback",
        }
    )


def handle_update(update: telegram.Update) -> ResponseBuilder:
    def handle(res: Response) -> Response:
        if (
            not update.get("callback_query")
            or get_telegram_update(update["update_id"]).exists
        ):
            return res
        else:
            return {
                **res,
                "update": update,
                "results": {
                    **res.get("results", {}),
                    "update_id": create_telegram_update(update),
                },
            }

    return handle


def handle_echo(update: telegram.Update) -> ResponseBuilder:
    def handle(res: Response) -> Response:
        if res.get("update"):
            callback_query_id, data = get_callback_query(update)
            answer_callback(callback_query_id)
            _send(lambda res: {**res, "text": f"`{json.dumps(data)}`"})
            return {
                **res,
                "data": data,
            }
        else:
            return res

    return handle


def handle_prepared_order(res: Response) -> Response:
    if res.get("data"):
        return {
            **res,
            "prepared_order": get_prepared_order(res["data"]["v"]),
        }
    else:
        return res


def handle_create_order(res: Response) -> Response:
    if res.get("prepared_order"):
        with netsuite_session() as session:
            try:
                order = create_sales_order(
                    session,
                    build_sales_order_from_prepared(
                        session, res["prepared_order"].to_dict()["order"]
                    ),
                )
                update_prepared_order_created(res["prepared_order"].id)
                send_created_order(order)
                return {
                    **res,
                    "results": {
                        **res.get("results", {}),
                        "order": order,
                    },
                }

            except Exception as e:
                print(e)
                send_create_order_error(e, res["prepared_order"].id)
                return res
    else:
        return res


def handle_cleanup(res: Response) -> Response:
    if res.get("prepared_order"):
        return {
            **res,
            "prepared_order": res["prepared_order"].to_dict(),
        }
    else:
        return res
