from typing import Any, Union
import os
import time
import hashlib
import hmac

import requests
from returns.result import ResultE, Success, safe
from returns.iterables import Fold

from db.firestore import DB
from shopee import shopee

BASE_URL = "https://partner.shopeemobile.com"
API_PATH = "api/v2"
PARTNER_ID = 2002943
SHOP_ID = 179124960
TIME_RANGE_FIELD = "create_time"
PAGE_SIZE = 100
BATCH_SIZE = 45

SHOPEE = DB.document("Shopee")


def sign_params(
    uri: str,
    access_token: str,
    shop_id: Union[int, str],
    params: dict[str, Union[int, str]],
) -> dict[str, Any]:
    ts = int(time.time())
    return {
        "partner_id": PARTNER_ID,
        "timestamp": ts,
        **({"shop_id": shop_id} if shop_id else {}),
        **({"access_token": access_token} if access_token else {}),
        **params,
        "sign": hmac.new(
            os.getenv("SHOPEE_API_KEY", "").encode("utf-8"),
            f"{PARTNER_ID}/{API_PATH}/{uri}{ts}{access_token}{shop_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest(),
    }


def build_shopee_request(
    access_token: str = "",
    shop_id_position: str = "query",
) -> shopee.RequestBuilder:
    def _build(
        uri: str,
        method: str = "GET",
        params: dict[str, Union[int, str]] = {},
        body: dict[str, Union[int, str]] = {},
    ) -> requests.PreparedRequest:
        return requests.Request(
            method,
            url=f"{BASE_URL}/{API_PATH}/{uri}",
            params=sign_params(
                uri,
                access_token,
                SHOP_ID if shop_id_position == "query" else "",
                params,
            ),
            json={
                **body,
                **(
                    {
                        "shop_id": SHOP_ID,
                        "partner_id": PARTNER_ID,
                    }
                    if shop_id_position == "body"
                    else {}
                ),
            },
            headers={
                "Content-Type": "application/json",
            },
        ).prepare()

    return _build


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
