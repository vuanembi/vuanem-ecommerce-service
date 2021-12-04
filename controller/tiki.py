from typing import Union

import requests
from requests_oauthlib import OAuth1Session

from libs.firestore import add_ack, get_latest_ack_id
from libs import tiki
from libs.netsuite import (
    get_customer_if_not_exist,
    map_sku_to_item_id,
    create_sales_order,
)
from libs.restlet import netsuite_session
from libs.telegram import send_created_order, send_new_order

from models import order, ecommerce, customer


def handle_event_queue() -> dict:
    with requests.Session() as session:
        ack_id, events = tiki.pull_events(session, get_latest_ack_id())
        orders = [
            tiki.get_order(session, event["payload"]["order_code"]) for event in events
        ]
        response: dict[str, Union[str, list[str]]] = {
            "controller": "tiki",
        }
        if orders:
            response["orders"] = handle_new_orders(orders)
        response["ack_id"] = add_ack(ack_id)

        return response


def handle_new_orders(orders):
    [send_new_order("Tiki", order) for order in orders]
    with netsuite_session() as oauth_session:
        created_sales_order = [
            create_sales_order(
                oauth_session,
                build_sales_order(oauth_session, order),
            )
            for order in orders
        ]
    [send_created_order("Tiki", id) for id in created_sales_order]
    return created_sales_order


def build_customer(session: OAuth1Session, tiki_order: tiki.Order) -> customer.Customer:
    return customer.build(
        get_customer_if_not_exist(
            session,
            customer.build_customer_request(
                tiki_order["shipping"]["address"]["full_name"],
                tiki_order["shipping"]["address"]["phone"],
            ),
        ),
        tiki_order["shipping"]["address"]["phone"],
        tiki_order["shipping"]["address"]["full_name"],
    )


def build_items(session: dict, tiki_order: tiki.Order) -> list[order.Item]:
    return [
        {
            "item": item,
            "quantity": quantity,
            "price": -1,
            "amount": amount / 1.1,
        }
        for item, quantity, amount in zip(
            [
                map_sku_to_item_id(session, i["product"]["seller_product_code"])
                for i in tiki_order["items"]
            ],
            [i["qty"] for i in tiki_order["items"]],
            [i["invoice"]["row_total"] for i in tiki_order["items"]],
        )
    ]


def build_sales_order(session: OAuth1Session, tiki_order: tiki.Order) -> order.Order:
    return order.build(
        build_customer(session, tiki_order),
        build_items(session, tiki_order),
        ecommerce.Tiki,
        f"tiki - {tiki_order['code']}"
    )
