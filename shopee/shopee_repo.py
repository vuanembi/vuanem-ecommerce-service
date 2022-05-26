from typing import Any, Union
import os
import time
import hashlib
import hmac

import requests
from returns.result import ResultE, Success, safe
from returns.iterables import Fold

from common.seller import Seller
from db.firestore import DB
from shopee import shopee

BASE_URL = "https://partner.shopeemobile.com"
API_PATH = "api/v2"
PARTNER_ID = 2002943
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
    seller: Seller,
    access_token: str = "",
    shop_id_position: str = "query",
) -> shopee.RequestBuilder:
    def _build(
        uri: str,
        method: str = "GET",
        params: dict[str, Union[int, str]] = {},
        body: dict[str, Union[int, str]] = {},
    ) -> requests.PreparedRequest:
        shop_id = seller.id if seller.id else 0
        return requests.Request(
            method,
            url=f"{BASE_URL}/{API_PATH}/{uri}",
            params=sign_params(
                uri,
                access_token,
                shop_id if shop_id_position == "query" else "",
                params,
            ),
            json={
                **body,
                **(
                    {
                        "shop_id": shop_id,
                        "partner_id": PARTNER_ID,
                    }
                    if shop_id_position == "body"
                    else {}
                ),
            },
            headers={"Content-Type": "application/json"},
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
            "update_time": order["update_time"],
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
        return Fold.collect_all(  # type: ignore
            [
                get_orders_batch_item(session, request_builder, ordersn_batch)
                for ordersn_batch in ordersn_batches
            ],
            Success(()),
        ).map(lambda x: [i for j in x for i in j])

    return _get


def get_item_list(
    session: requests.Session,
    request_builder: shopee.RequestBuilder,
):
    @safe
    def _get():
        def __get(offset: int = 1) -> list[int]:
            with session.send(
                request_builder(
                    "product/get_item_list",
                    method="GET",
                    params={
                        "page_size": PAGE_SIZE,
                        "item_status": "NORMAL",
                        "offset": offset,
                    },
                )
            ) as r:
                r.raise_for_status()
                res = r.json()
            if res["error"]:
                raise requests.exceptions.HTTPError(res)
            items = [i["item_id"] for i in res["response"]["item"]]
            return (
                items
                if not res["response"]["has_next_page"]
                else items + __get(res["response"]["next_offset"])
            )

        return __get()

    return _get


@safe
def get_items_batch_info(
    session: requests.Session,
    request_builder: shopee.RequestBuilder,
    item_list: list[int],
) -> list[dict[str, Any]]:
    with session.send(
        request_builder(
            "product/get_item_base_info",
            method="GET",
            params={
                "item_id_list": ",".join([str(i) for i in item_list]),
            },
        )
    ) as r:
        r.raise_for_status()
        res = r.json()
    if res["error"]:
        raise requests.exceptions.HTTPError(res)
    return [
        {
            "item_id": row.get("item_id"),
            "category_id": row.get("category_id"),
            "item_name": row.get("item_name"),
            "item_sku": row.get("item_sku"),
            "create_time": row.get("create_time"),
            "update_time": row.get("update_time"),
            "attribute_list": [
                {
                    "attribute_id": attribute.get("attribute_id"),
                    "original_attribute_name": attribute.get("original_attribute_name"),
                    "is_mandatory": attribute.get("is_mandatory"),
                    "attribute_value_list": [
                        {
                            "value_id": value.get("value_id"),
                            "original_value_name": value.get("original_value_name"),
                            "value_unit": value.get("value_unit"),
                        }
                        for value in attribute["attribute_value_list"]
                    ]
                    if attribute.get("attribute_value_list")
                    else [],
                }
                for attribute in row["attribute_list"]
            ]
            if row.get("attribute_list")
            else [],
            "price_info": [
                {
                    "currency": info.get("currency"),
                    "original_price": info.get("original_price"),
                    "current_price": info.get("current_price"),
                }
                for info in row["price_info"]
            ]
            if row.get("price_info")
            else [],
            "stock_info": [
                {
                    "stock_type": info.get("stock_type"),
                    "current_stock": info.get("current_stock"),
                    "normal_stock": info.get("normal_stock"),
                    "reserved_stock": info.get("reserved_stock"),
                }
                for info in row["stock_info"]
            ]
            if row.get("stock_info")
            else [],
            "weight": row.get("weight"),
            "dimension": {
                "package_length": row["dimension"].get("package_length"),
                "package_width": row["dimension"].get("package_width"),
                "package_height": row["dimension"].get("package_height"),
            }
            if row.get("dimension")
            else {},
            "logistic_info": [
                {
                    "logistic_id": info.get("logistic_id"),
                    "logistic_name": info.get("logistic_name"),
                    "enabled": info.get("enabled"),
                    "shipping_fee": info.get("shipping_fee"),
                    "is_free": info.get("is_free"),
                }
                for info in row["logistic_info"]
            ]
            if row.get("logistic_info")
            else [],
            "pre_order": {
                "is_pre_order": row["pre_order"].get("is_pre_order"),
                "days_to_ship": row["pre_order"].get("days_to_ship"),
            }
            if row.get("pre_order")
            else {},
            "condition": row.get("condition"),
            "size_chart": row.get("size_chart"),
            "item_status": row.get("item_status"),
            "has_model": row.get("has_model"),
            "promotion_id": row.get("promotion_id"),
            "brand": {
                "brand_id": row["brand"].get("brand_id"),
                "original_brand_name": row["brand"].get("original_brand_name"),
            }
            if row.get("brand")
            else {},
        }
        for row in res["response"]["item_list"]
    ]


def get_items_info(
    session: requests.Session,
    request_builder: shopee.RequestBuilder,
):
    def _get(item_list: list[int]) -> ResultE[list[dict[str, Any]]]:
        item_list_batches = [
            item_list[i : i + BATCH_SIZE] for i in range(0, len(item_list), BATCH_SIZE)
        ]
        return Fold.collect_all(  # type: ignore
            [
                get_items_batch_info(session, request_builder, item_list_batch)
                for item_list_batch in item_list_batches
            ],
            Success(()),
        ).map(lambda x: [i for j in x for i in j])

    return _get
