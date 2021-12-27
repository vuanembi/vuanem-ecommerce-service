from typing import Callable, Optional

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success, safe
from returns.pointfree import bind, map_
from returns.pipeline import flow
from returns.functions import raise_exception

from tiki import tiki, auth_repo, data_repo
from netsuite import netsuite, prepare_repo, restlet_repo
from telegram import telegram_service


def auth_service() -> OAuth2Session:
    return auth_repo.get_access_token().bind(auth_repo.get_auth_session)


def _add_customer(order: tiki.Order) -> netsuite.PreparedCustomer:
    return prepare_repo.build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def _add_items(order: tiki.Order) -> netsuite.Items:
    with restlet_repo.netsuite_session() as session:
        return {
            "item": [
                i
                for i in [
                    prepare_repo.build_item(item, quantity, amount)
                    for item, quantity, amount in zip(
                        [
                            prepare_repo.map_sku_to_item_id(
                                session, i["product"]["seller_product_code"]
                            ).unwrap()
                            for i in order["items"]
                        ],
                        [i["seller_income_detail"]["item_qty"] for i in order["items"]],
                        [
                            i["seller_income_detail"]["sub_total"]
                            for i in order["items"]
                        ],
                    )
                ]
                if i
            ]
        }


def _build_order(order: tiki.Order) -> netsuite.PreparedOrder:
    return flow(
        {},
        prepare_repo.build_prepared_order(_add_items, order),
        prepare_repo.build_prepared_order(_add_customer, order),
        prepare_repo.build_prepared_order(
            prepare_repo.build_prepared_order_meta,
            f"tiki - {order['code']}",
        ),
        prepare_repo.build_prepared_order(lambda _: netsuite.TikiEcommerce),
    )


def _handle_order(order: tiki.Order) -> ResultE[str]:
    return flow(
        order,
        data_repo.persist_tiki_order,
        map_(_build_order),
        bind(prepare_repo.persist_prepared_order),
        map_(lambda x: x.id),
    )


def pull_service(
    session: OAuth2Session,
) -> tuple[ResultE[str], ResultE[list[tiki.Event]]]:
    return (
        data_repo.get_ack_id()
        .bind(data_repo.get_events(session))
        .lash(raise_exception)
        .bind(lambda x: (Success(x[0]), Success(x[1])))
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
            telegram_service.send_new_order("Tiki", order.unwrap(), id)
            for order, id in zip(orders, persisted_orders)
        ]
        return {
            "orders": persisted_orders,
        }

    return _svc


def ack_service(ack_id: Success[Optional[str]]) -> Callable[[str], ResultE[dict]]:
    @safe
    def _svc(res: dict = {}) -> dict:
        return {
            **res,
            "ack": data_repo.update_ack_id(ack_id).unwrap(),
        }

    return _svc
