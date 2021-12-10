import requests

from libs.firestore import (
    create_tiki_ack_id,
    create_prepared_order,
    get_latest_tiki_ack_id,
)
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
from models.utils import Response


def tiki_controller() -> Response:
    return compose(handle_ack, handle_orders, handle_events,)(
        {
            "controller": "tiki",
        }
    )


def handle_events(res: Response) -> Response:
    with requests.Session() as session:
        ack_id, events = pull_events(session, get_latest_tiki_ack_id())
        orders = [
            get_order(
                session,
                event["payload"]["order_code"],
            )
            for event in events
        ]
    return {
        **res,
        "ack_id": ack_id,
        "orders": orders,
    }


def handle_orders(res: Response) -> Response:
    if len(res["orders"]):
        prepared_order_ids = [
            create_prepared_order(order)
            for order in [build_prepared_components(order) for order in res["orders"]]
        ]
        print(prepared_order_ids)
        [
            send_new_order("Tiki", order, prepared_order_id)
            for order, prepared_order_id in zip(res["orders"], prepared_order_ids)
        ]
        return {
            **res,
            "results": {
                **res.get("results", {}),
                "orders": prepared_order_ids,
            },
        }
    else:
        return res


def handle_ack(res: dict) -> Response:
    return {
        **res,
        "results": {
            **res.get("results", {}),
            "ack_id": create_tiki_ack_id(res["ack_id"]),
        },
    }


def build_prepared_components(tiki_order: tiki.Order) -> order.Order:
    return compose(
        build_prepared_order(add_items, tiki_order),
        build_prepared_order(add_customer, tiki_order),
        build_prepared_order(build_prepared_order_meta, f"tiki - {tiki_order['code']}"),
        build_prepared_order(lambda _: ecommerce.Tiki),
    )({})


def add_customer(order: tiki.Order) -> customer.PreparedCustomer:
    return build_prepared_customer(
        order["shipping"]["address"]["phone"],
        order["shipping"]["address"]["full_name"],
    )


def add_items(order: tiki.Order) -> order.Items:
    with netsuite_session() as session:
        return {
            "item": [
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
