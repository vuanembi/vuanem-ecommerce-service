import time
from datetime import datetime

import requests
from returns.result import ResultE, Success, safe
from returns.iterables import Fold
from google.cloud import firestore

from shopee import shopee, shopee_repo

TIME_RANGE_FIELD = "create_time"
PAGE_SIZE = 100
BATCH_SIZE = 45

ORDER = shopee_repo.SHOPEE.collection("Order")


def get_orders(session: requests.Session, request_builder: shopee.RequestBuilder):
    @safe
    def _get(time_from: int):
        def __get(cursor: str = "") -> list[shopee.OrderSN]:
            with session.send(
                request_builder(
                    "order/get_order_list",
                    method="GET",
                    params={
                        "time_range_field": TIME_RANGE_FIELD,
                        "page_size": PAGE_SIZE,
                        "time_from": time_from,
                        "time_to": int(time.time()),
                        "cursor": cursor,
                    },
                )
            ) as r:
                r.raise_for_status()
                res = r.json()
            if res["error"]:
                raise requests.exceptions.HTTPError(res)
            orders = [i["order_sn"] for i in res["response"]["order_list"]]
            return (
                orders
                if not res["response"]["more"]
                else orders + __get(res["response"]["next_cursor"])
            )

        return __get()

    return _get


@safe
def get_orders_batch_item(
    session: requests.Session,
    request_builder: shopee.RequestBuilder,
    order_sns: list[shopee.OrderSN],
) -> list[shopee.Order]:
    with session.send(
        request_builder(
            "order/get_order_detail",
            method="GET",
            params={
                "response_optional_fields": "item_list",
                "order_sn_list": ",".join(order_sns),
            },
        )
    ) as r:
        r.raise_for_status()
        res = r.json()
    if res["error"]:
        raise requests.exceptions.HTTPError(res)
    return [
        {
            "order_sn": order["order_sn"],
            "create_time": order["create_time"],
            "item_list": [
                {
                    "item_name": item["item_name"],
                    "item_sku": item["item_sku"],
                    "model_quantity_purchased": item["model_quantity_purchased"],
                    "model_original_price": item["model_original_price"],
                    "model_discounted_price": item["model_discounted_price"],
                }
                for item in order["item_list"]
            ],
        }
        for order in res["response"]["order_list"]
    ]


def get_order_items(
    session: requests.Session,
    request_builder: shopee.RequestBuilder,
):
    def _get(order_sns: list[shopee.OrderSN]) -> ResultE[list[shopee.Order]]:
        ordersn_batches = [
            order_sns[i : i + BATCH_SIZE] for i in range(0, len(order_sns), BATCH_SIZE)
        ]
        return Fold.collect_all(
            [
                get_orders_batch_item(session, request_builder, ordersn_batch)
                for ordersn_batch in ordersn_batches
            ],
            Success(()),
        ).map(lambda x: [i for j in x for i in j])

    return _get


@safe
def persist_order(order: shopee.Order) -> shopee.Order:
    doc_ref = ORDER.document()
    doc_ref.create(
        {
            "order": order,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )
    return order


@safe
def get_max_created_at() -> datetime:
    return shopee_repo.SHOPEE.get(["state.max_created_at"]).get("state.max_created_at")


@safe
def persist_max_created_at(orders: list[shopee.Order]) -> list[shopee.Order]:
    if orders:
        shopee_repo.SHOPEE.set(
            {
                "state": {
                    "max_created_at": max([order["create_time"] for order in orders]),
                },
            },
            merge=True,
        )
    return orders
