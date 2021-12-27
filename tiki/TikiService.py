from typing import Callable, Optional

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success, safe
from returns.pointfree import bind
from returns.pipeline import flow
from returns.functions import raise_exception

from tiki import Tiki, TikiAuthRepo, TikiDataRepo
from netsuite import NetSuite, NetSuitePrepareRepo, RestletRepo
from telegram import TelegramService


def auth_service() -> OAuth2Session:
    return TikiAuthRepo.get_access_token().bind(TikiAuthRepo.get_auth_session)


def _add_customer(order: Tiki.Order) -> NetSuite.PreparedCustomer:
    return NetSuitePrepareRepo.build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def _add_items(order: Tiki.Order) -> NetSuite.Items:
    with RestletRepo.netsuite_session() as session:
        return {
            "item": [
                i
                for i in [
                    NetSuitePrepareRepo.build_item(item, quantity, amount)
                    for item, quantity, amount in zip(
                        [
                            NetSuitePrepareRepo.map_sku_to_item_id(
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


def _build_order(order: Tiki.Order) -> NetSuite.PreparedOrder:
    return flow(
        {},
        NetSuitePrepareRepo.build_prepared_order(_add_items, order),
        NetSuitePrepareRepo.build_prepared_order(_add_customer, order),
        NetSuitePrepareRepo.build_prepared_order(
            NetSuitePrepareRepo.build_prepared_order_meta,
            f"tiki - {order['code']}",
        ),
        NetSuitePrepareRepo.build_prepared_order(lambda _: NetSuite.TikiEcommerce),
    )


def _handle_order(order: Tiki.Order) -> ResultE[str]:
    return flow(  # type: ignore
        order,
        TikiDataRepo.persist_tiki_order,
        bind(_build_order),
        NetSuitePrepareRepo.persist_prepared_order,
        bind(lambda x: Success(x.id)),
    )


def pull_service(
    session: OAuth2Session,
) -> tuple[ResultE[str], ResultE[list[Tiki.Event]]]:
    return (
        TikiDataRepo.get_ack_id()
        .bind(TikiDataRepo.get_events(session))
        .lash(raise_exception)
        .bind(lambda x: (Success(x[0]), Success(x[1])))
    )


def events_service(
    session: OAuth2Session,
) -> Callable[[list[Tiki.Event]], ResultE[dict]]:
    @safe
    def _svc(events: list[Tiki.Event]) -> dict:
        orders = [
            TikiDataRepo.get_order(session)(TikiDataRepo.extract_order(e))
            for e in events
        ]
        persisted_orders = [order.bind(_handle_order).unwrap() for order in orders]
        [
            TelegramService.send_new_order("Tiki", order.unwrap(), id)
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
            "ack": ack_id.bind(TikiDataRepo.update_ack_id).unwrap(),
        }

    return _svc
