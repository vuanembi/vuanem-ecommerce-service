from typing import Callable, Optional

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success, safe
from returns.pointfree import bind, map_
from returns.pipeline import flow
from returns.functions import raise_exception

from tiki import tiki, auth_repo, data_repo
from netsuite import netsuite, netsuite_service, prepare_repo
from telegram import message_service


def auth_service() -> OAuth2Session:
    return auth_repo.get_access_token().map(auth_repo.get_auth_session).unwrap()


_build_prepared_order = netsuite_service.build_prepared_order_service(
    items_fn=lambda x: x["items"],
    item_sku_fn=lambda x: x["product"]["seller_product_code"],
    item_qty_fn=lambda x: x["seller_income_detail"]["item_qty"],
    item_amt_fn=lambda x: x["seller_income_detail"]["sub_total"],
    ecom=netsuite.TikiEcommerce,
    memo_builder=lambda x: f"tiki - {x['code']}",
    customer_builder=lambda x: prepare_repo.build_customer(
        x["shipping"]["address"]["phone"],
        x["shipping"]["address"]["full_name"],
    ),
)


def _handle_order(order: tiki.Order) -> ResultE[str]:
    return flow(
        order,
        data_repo.persist_tiki_order,
        bind(_build_prepared_order),
        bind(prepare_repo.persist_prepared_order),
        map_(lambda x: x.id), # type: ignore
    )


def pull_service(
    session: OAuth2Session,
) -> tuple[ResultE[str], ResultE[list[tiki.Event]]]:
    return (
        data_repo.get_ack_id()
        .bind(data_repo.get_events(session))
        .lash(raise_exception)
        .bind(lambda x: (Success(x[0]), Success(x[1]))) # type: ignore
    )


def events_service(
    session: OAuth2Session,
) -> Callable[[list[tiki.Event]], ResultE[dict]]:
    @safe
    def _svc(events: list[tiki.Event]) -> dict:
        orders = [
            data_repo.get_order(session)(data_repo.extract_order(e)) for e in events
        ]
        persisted_orders = [order.bind(_handle_order).unwrap() for order in orders]
        [
            message_service.send_new_order("Tiki", order.unwrap(), id) # type: ignore
            for order, id in zip(orders, persisted_orders)
        ]
        return {
            "orders": persisted_orders,
        }

    return _svc


def ack_service(ack_id: str) -> Callable[[dict], ResultE[dict]]:
    @safe
    def _svc(res: dict = {}) -> dict:
        return {
            **res,
            "ack": data_repo.update_ack_id(ack_id).unwrap(),
        }

    return _svc
