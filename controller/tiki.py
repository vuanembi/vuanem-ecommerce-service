from typing import Optional

import requests

from libs.firestore import add_ack, get_latest_ack_id
from libs.tiki import pull_events, get_order
from libs.netsuite import (
    build_item,
    build_prepared_customer,
    build_prepared_order_meta,
    build_prepared_order,
    map_sku_to_item_id,
)
from libs.restlet import netsuite_session
from libs.telegram import send_new_order
from libs.utils import compose

from models.netsuite import order, customer, ecommerce
from models.ecommerce import tiki
from models.utils import ResponseBuilder


def tiki_controller() -> dict:
    with requests.Session() as session:
        ack_id, events = pull_events(session, get_latest_ack_id())
        orders = [
            get_order(
                session,
                event["payload"]["order_code"],
            )
            for event in events
        ]
    print(orders)
    return compose(handle_orders(orders), ack_ack_id(ack_id))(
        {
            "controller": "tiki",
        }
    )


def handle_orders(orders: list[tiki.Order]) -> ResponseBuilder:
    def handle(res: dict) -> dict:
        if len(orders):
            prepared_order_ids = [build_prepared_components(order) for order in orders]
            [send_new_order("Tiki", order) for order in orders]
            return {
                **res,
                "orders": prepared_order_ids,
            }
        else:
            return res

    return handle


def ack_ack_id(ack_id: str) -> ResponseBuilder:
    def ack(res: dict) -> dict:
        return {
            **res,
            "ack_id": add_ack(ack_id),
        }

    return ack


def build_prepared_components(order: tiki.Order) -> order.Order:
    build = compose(
        build_prepared_order(add_customer, order),
        build_prepared_order(add_items, order),
        build_prepared_order(lambda _: ecommerce.Tiki),
        build_prepared_order(build_prepared_order_meta, f"tiki - {order['code']}"),
    )
    return build({})


def add_customer(order: tiki.Order) -> customer.PreparedCustomer:
    return build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def add_items(order: tiki.Order) -> order.Items:
    with netsuite_session() as session:
        return {
            "items": [
                i
                for i in [
                    build_item(item, quantity, amount)
                    for item, quantity, amount in zip(
                        [
                            map_sku_to_item_id(
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
