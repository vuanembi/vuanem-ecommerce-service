from requests import Session

from returns.result import Success, safe
from returns.pointfree import bind, lash
from returns.pipeline import flow

from tiki import Tiki, TikiAuthRepo, TikiDataRepo
from restlet import RestletRepo
from netsuite import NetSuite, NetSuitePrepareRepo


def _persist_new_access_token(*args) -> Success[dict]:
    return flow(
        None,
        TikiAuthRepo.get_new_access_token,
        bind(TikiAuthRepo.persist_access_token),
        bind(lambda doc: Success(doc.get().to_dict()["access_token"])),
        bind(lambda x: Success(TikiAuthRepo.build_headers(x))),
    )


def authenticate(session: Session) -> dict:
    return flow(  # type: ignore
        None,
        TikiAuthRepo.get_latest_access_token,
        bind(lambda doc: Success(doc.to_dict()["access_token"])),
        bind(lambda x: Success(TikiAuthRepo.build_headers(x))),
        bind(TikiDataRepo.get_seller_info(session)),
        lash(_persist_new_access_token),
    ).unwrap()


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
                            )
                            for i in order["items"]
                        ],
                        [i["qty"] for i in order["items"]],
                        [i["invoice"]["row_total"] for i in order["items"]],
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


def _handle_order(session, id):
    return flow(
        id,
        TikiDataRepo.get_order(session),
        bind(_build_order),
        NetSuitePrepareRepo.persist_prepared_order,
        bind(lambda x: Success(x.id)),
    ).unwrap()


def get_events(session) -> tuple[Success[str], Success[list[Tiki.Event]]]:
    return (
        TikiDataRepo.get_latest_ack_id()
        .bind(lambda x: Success(x.id))
        .bind(TikiDataRepo.get_events(session))
        # .bind(lambda x: (Success(x[0]), Success(x[1])))
        .bind(lambda x: (Success(x[0]), Success(x[1][:2])))
    )


def events_service(session):
    @safe
    def _svc(events: list[Tiki.Event]):
        return {
            "orders": [
                _handle_order(session, order)
                for order in [TikiDataRepo.extract_order(e) for e in events]
            ],
        }

    return _svc


def ack_service(ack_id: Success[str]):
    @safe
    def _svc(res: dict = {}):
        return {
            **res,
            "ack": ack_id.bind(TikiDataRepo.persist_ack_id)
            .bind(lambda x: Success(x.id))
            .unwrap(),
        }

    return _svc
