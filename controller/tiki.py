from typing import Union

import requests

from libs.firestore import add_ack, get_latest_ack_id
from libs import tiki
from libs.netsuite import map_sku_to_item_id
from libs.restlet import netsuite_session
from libs.telegram import send_created_order, send_new_order

from models.netsuite import order, customer, ecommerce


def handle_event_queue() -> dict:
    with requests.Session() as session:
        ack_id, events = tiki.pull_events(session, get_latest_ack_id())
        orders = [
            tiki.get_order(session, event["payload"]["order_code"]) for event in events
        ]
        print(orders)
        response: dict[str, Union[str, list[str]]] = {
            "controller": "tiki",
        }
        if orders:
            response["orders"] = handle_new_orders(orders)
        response["ack_id"] = add_ack(ack_id)

        return response


def handle_new_orders(orders: list[tiki.Order]) -> list[str]:
    prepared_order_ids = [build_prepared_order(order) for order in orders]
    [send_new_order("Tiki", order) for order in orders]
    return prepared_order_ids


def build_customer(order: tiki.Order) -> customer.PreparedCustomer:
    return customer.build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def build_items(order: tiki.Order) -> list[order.Item]:
    with netsuite_session() as session:
        return [
            order.build_item(item, quantity, amount)
            for item, quantity, amount in zip(
                [
                    map_sku_to_item_id(session, i["product"]["seller_product_code"])
                    for i in order["items"]
                ],
                [i["qty"] for i in order["items"]],
                [i["invoice"]["row_total"] for i in order["items"]],
            )
        ]


def build_prepared_order(order: tiki.Order) -> order.Order:
    return order.build(
        build_customer(order),
        build_items(order),
        ecommerce.Tiki,
        f"tiki - {order['code']}",
    )
