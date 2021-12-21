from requests import Session

from returns.io import IOResultE, IOSuccess, impure, impure_safe
from returns.pointfree import bind, lash
from returns.pipeline import flow
from returns.unsafe import unsafe_perform_io

from tiki import Tiki, TikiAuthRepo, TikiDataRepo
from restlet import RestletRepo
from netsuite import NetSuite, NetSuitePrepareRepo


def persist_new_access_token(*args) -> IOSuccess[dict]:
    return flow(
        None,
        TikiAuthRepo.get_new_access_token,
        bind(TikiAuthRepo.persist_access_token),
        bind(lambda doc: IOSuccess(doc.get().to_dict()["access_token"])),
        bind(lambda x: IOSuccess(TikiAuthRepo.build_headers(x))),
    )


def authenticate(session: Session) -> IOSuccess[dict]:
    return flow(
        None,
        TikiAuthRepo.get_latest_access_token,
        bind(lambda doc: IOSuccess(doc.to_dict()["access_token"])),
        bind(lambda x: IOSuccess(TikiAuthRepo.build_headers(x))),
        bind(TikiDataRepo.get_seller_info(session)),
        lash(persist_new_access_token),
        bind(lambda x: x),
    )


def add_customer(order: Tiki.Order) -> NetSuite.PreparedCustomer:
    return NetSuitePrepareRepo.build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def add_items(order: Tiki.Order) -> NetSuite.Items:
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


def build_prepared_order(order: Tiki.Order) -> NetSuite.PreparedOrder:
    return flow(
        {},
        NetSuitePrepareRepo.build_prepared_order(add_items, order),
        NetSuitePrepareRepo.build_prepared_order(add_customer, order),
        NetSuitePrepareRepo.build_prepared_order(
            NetSuitePrepareRepo.build_prepared_order_meta,
            f"tiki - {order['code']}",
        ),
        NetSuitePrepareRepo.build_prepared_order(lambda _: NetSuite.TikiEcommerce),
    )


def persist_prepared_order(session, headers, id):
    return flow(
        id,
        TikiDataRepo.get_order(session, headers),
        bind(build_prepared_order),
        NetSuitePrepareRepo.persist_prepared_order,
    )
