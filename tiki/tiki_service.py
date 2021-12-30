from typing import Callable

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success
from returns.pointfree import bind, map_
from returns.pipeline import flow
from returns.iterables import Fold
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
    ecom=netsuite.TIKI_ECOMMERCE,
    memo_builder=lambda x: f"tiki - {x['code']}",
    customer_builder=lambda x: prepare_repo.build_customer(
        netsuite.TIKI_CUSTOMER,
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
        map_(lambda x: x.id),  # type: ignore
    )


def pull_service(session: OAuth2Session) -> ResultE[tiki.EventRes]:
    return (
        data_repo.get_ack_id().bind(data_repo.get_events(session)).lash(raise_exception)
    )


def order_service(session: OAuth2Session, events: list[tiki.Event]) -> ResultE[dict]:
    return Fold.collect_all(
        [
            x[1].apply(x[0].apply(Success(message_service.send_new_order("Tiki"))))
            for x in [
                (order, order.bind(_handle_order))
                for order in [
                    data_repo.get_order(session)(data_repo.extract_order(e))
                    for e in events
                ]
            ]
        ],
        Success(()),
    ).map(lambda x: {"orders": [y[1] for y in x]})


def ack_service(ack_id: str) -> Callable[[dict], ResultE[dict]]:
    def _svc(res: dict):
        return data_repo.update_ack_id(ack_id).map(
            lambda x: {
                **res,
                "ack": x,
            }
        )

    return _svc


def events_service(session: OAuth2Session):
    def _svc(event_res: tiki.EventRes) -> ResultE[dict]:
        ack_id, events = event_res
        return order_service(session, events).bind(ack_service(ack_id))

    return _svc
