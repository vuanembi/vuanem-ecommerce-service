import requests

from returns.pipeline import flow
from returns.pointfree import bind
from returns.maybe import Maybe, Some, Nothing
from returns.methods import unwrap_or_failure

from libs.restlet import netsuite_session
from libs.netsuite import (
    map_sku_to_item_id,
    build_item,
    build_prepared_order_meta,
    build_prepared_order,
)
from libs.shopee import get_order_details
from libs.firestore import create_shopee_push, get_shopee_push, create_prepared_order
from libs.telegram import send_new_order

from models.ecommerce import shopee
from models.netsuite import customer, ecommerce
from models.utils import Response


def shopee_controller(request_data: shopee.OrderStatusPush) -> dict:
    return {
        "controller": "shopee",
        "results": unwrap_or_failure(
            flow(
                request_data,
                validate_order_code,
                bind(validate_order_status),
                bind(get_push_order_id),
                bind(get_push_order),
                bind(build_prepared_components),
                bind(create_prepared_component),
                bind(send_telegram),
            )
        ),
    }


def validate_order_code(push: shopee.OrderStatusPush) -> Maybe[shopee.OrderStatusPush]:
    return Some(push) if push["code"] == 3 else Nothing


def validate_order_status(
    push: shopee.OrderStatusPush,
) -> Maybe[shopee.OrderStatusPush]:
    return Some(push) if push["data"]["status"] == "UNPAID" else Nothing


def get_push_order_id(push: shopee.OrderStatusPush) -> Maybe[str]:
    return Some(push["data"]["ordersn"])


def validate_order_id(ordersn: str) -> Maybe[str]:
    order_ref = get_shopee_push(ordersn)
    if order_ref.exists:
        return Nothing
    else:
        return Some(create_shopee_push(ordersn))


def get_push_order(ordersn: str) -> Maybe[shopee.Order]:
    with requests.Session() as session:
        return Some(get_order_details(session, ordersn))


def build_prepared_components(shopee_order: shopee.Order) -> Response:
    return Some(
        {
            "order": shopee_order,
            "prepared_order": flow(
                {},
                build_prepared_order(add_items, shopee_order),
                build_prepared_order(lambda _: customer.ShopeeMock),
                build_prepared_order(
                    build_prepared_order_meta, f"shopee - {shopee_order['ordersn']}"
                ),
                build_prepared_order(lambda _: ecommerce.Shopee),
            ),
        }
    )


def add_items(order: shopee.Order):
    with netsuite_session() as session:
        return {
            "item": [
                i
                for i in [
                    build_item(item, quantity, int(amount))
                    for item, quantity, amount in zip(
                        [
                            map_sku_to_item_id(session, i["variation_sku"])
                            for i in order["items"]
                        ],
                        [i["variation_quantity_purchased"] for i in order["items"]],
                        [i["variation_discounted_price"] for i in order["items"]],
                    )
                ]
                if i
            ]
        }


def create_prepared_component(res: Response) -> Maybe[Response]:
    return Some(
        {
            "order": res["order"],
            "results": {
                "order": create_prepared_order(res["order"]),
            },
        }
    )


def send_telegram(res: Response) -> Maybe[Response]:
    send_new_order("Shopee", res["order"], res["results"]["order"])
    return Some(res)
