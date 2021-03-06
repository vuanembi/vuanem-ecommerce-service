from typing import Any, Callable, Optional
import os
import time
import hashlib
import hmac
from datetime import datetime

import requests
from dateutil import parser
import pytz
import requests
from returns.result import safe

from lazada import lazada

LAZ_APP_KEY = "104842"
PAGE_LIMIT = 100


def build_lazada_request(
    base_url: str,
    access_token: Optional[lazada.AccessToken] = None,
) -> Callable[[str, dict[str, Any]], requests.PreparedRequest]:
    def _build(uri: str, params: dict[str, Any]) -> requests.PreparedRequest:
        return requests.Request(
            "GET",
            url=f"{base_url}{uri}",
            params=sign_params(
                uri,
                {
                    **params,
                    "access_token": access_token["access_token"],
                }
                if access_token
                else params,
            ),
        ).prepare()

    return _build


def sign_params(uri: str, params: dict[str, Any]) -> dict[str, Any]:
    all_params = dict(
        sorted(
            {
                **params,
                "app_key": LAZ_APP_KEY,
                "timestamp": int(round(time.time())) * 1000,
                "sign_method": "sha256",
            }.items()
        )
    )
    return {
        **all_params,
        "sign": hmac.new(
            os.getenv("LAZ_APP_SECRET", "").encode("utf-8"),
            (uri + "".join([f"{k}{v}" for k, v in all_params.items()])).encode("utf-8"),
            hashlib.sha256,
        )
        .hexdigest()
        .upper(),
    }


def parse_timestamp(x: str) -> Optional[datetime]:
    try:
        return parser.parse(x).astimezone(pytz.utc).replace(tzinfo=None) if x else None
    except:
        return None


def get_auth_builder(token: lazada.AccessToken) -> lazada.AuthBuilder:
    return build_lazada_request("https://api.lazada.vn/rest", token)


def get_orders(session: requests.Session, auth_builder: lazada.AuthBuilder):
    @safe
    def _get(created_after: datetime):
        def __get(offset: int = 0):
            with session.send(
                auth_builder(
                    "/orders/get",
                    {
                        "created_after": created_after.isoformat(timespec="seconds")
                        + "Z",
                        "limit": PAGE_LIMIT,
                        "offset": offset,
                    },
                )
            ) as r:
                res = r.json()
            orders = [
                {
                    "order_id": order["order_id"],
                    "created_at": parse_timestamp(order["created_at"]),
                    "updated_at": parse_timestamp(order["updated_at"]),
                }
                for order in res["data"]["orders"]
                if parse_timestamp(order["created_at"]) != created_after
            ]
            return orders if not orders else orders + __get(offset + PAGE_LIMIT)

        return __get()

    return _get


@safe
def get_order_item(
    session: requests.Session,
    auth_builder: lazada.AuthBuilder,
    order_id: int,
):
    with session.send(
        auth_builder(
            "/order/items/get",
            {"order_id": order_id},
        )
    ) as r:
        res = r.json()
    return [
        {
            "sku": item["sku"],
            "name": item["name"],
            "paid_price": item["paid_price"],
            "voucher_platform": item["voucher_platform"],
        }
        for item in res["data"]
    ]


def get_products(session: requests.Session, auth_builder: lazada.AuthBuilder):
    @safe
    def _get():
        def __get(offset: int = 0):
            with session.send(
                auth_builder(
                    "/products/get",
                    {
                        "filter": "all",
                        "limit": 50,
                        "offset": offset,
                    },
                )
            ) as r:
                res = r.json()
            products = [
                {
                    "item_id": product["item_id"],
                    "created_time": datetime.utcfromtimestamp(
                        float(product["created_time"]) / 1000
                    ).isoformat(timespec="seconds"),
                    "updated_time": datetime.utcfromtimestamp(
                        float(product["updated_time"]) / 1000
                    ).isoformat(timespec="seconds"),
                    "skus": [
                        {
                            "Status": sku.get("Status"),
                            "quantity": sku.get("quantity"),
                            "SellerSku": sku.get("SellerSku"),
                            "ShopSku": sku.get("ShopSku"),
                            "Url": sku.get("Url"),
                            "multiWarehouseInventories": [
                                {
                                    "occupyQuantity": inv.get("occupyQuantity"),
                                    "quantity": inv.get("quantity"),
                                    "totalQuantity": inv.get("totalQuantity"),
                                    "withholdQuantity": inv.get("withholdQuantity"),
                                    "warehouseCode": inv.get("warehouseCode"),
                                    "sellableQuantity": inv.get("sellableQuantity"),
                                }
                                for inv in sku["multiWarehouseInventories"]
                            ]
                            if sku.get("multiWarehouseInventories")
                            else [],
                            "package_width": sku.get("package_width"),
                            "package_height": sku.get("package_height"),
                            "special_price": sku.get("special_price"),
                            "price": sku.get("price"),
                            "channelInventories": [
                                {
                                    "channelName": inv.get("channelName"),
                                    "startTime": inv.get("startTime"),
                                    "endTime": inv.get("endTime"),
                                    "sellableQuantity": inv.get("sellableQuantity"),
                                }
                                for inv in sku["channelInventories"]
                            ]
                            if sku.get("channelInventories")
                            else [],
                            "package_length": sku.get("package_length"),
                            "package_weight": sku.get("package_weight"),
                            "SkuId": sku.get("SkuId"),
                        }
                        for sku in product["skus"]
                    ]
                    if product.get("skus")
                    else [],
                    "primary_category": product["primary_category"],
                }
                for product in res["data"].get("products", [])
            ]
            return products if not products else products + __get(offset + 50)

        return __get()

    return _get
