from typing import Callable, Any
import os
import hmac
import hashlib
import json
from datetime import datetime

import requests
import pytz

from shopee import shopee

BASE_URL = "https://partner.shopeemobile.com"
API_PATH = "api/v2"
PARTNER_ID = 2002943
SHOP_ID = 179124960


def get_auth_builder(access_token: str = ""):
    def build(path: str):
        ts = str(int(datetime.now(pytz.timezone("Asia/Saigon")).timestamp()))
        sign = hmac.new(  # type: ignore
            os.getenv("SHOPEE_API_KEY", "").encode(),
            f"{PARTNER_ID}{path}{ts}{access_token}{SHOP_ID}",
            hashlib.sha256,
        ).hexdigest()
        return ts, access_token, sign
    return build

def shopee_request(session, auth_builder, path, body):
    ts, access_token, sign = auth_builder(f"/{API_PATH}/{path}")
    with session.post(
        f"{BASE_URL}/{API_PATH}/{path}",
        params={
            "partner_id": PARTNER_ID,
            "timestamp": ts,
            "access_token": access_token,
            "shop_id": SHOP_ID,
            "sign": sign
        }
    ) as r:
        res = r.json()


def sign(url: str, body: dict) -> str:
    return hmac.new(
        os.getenv("SHOPEE_API_KEY", "").encode(),
        msg=f"{url}|{json.dumps(body)}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def build_body(body: dict = {}) -> dict[str, Any]:
    return {
        **body,
        "partner_id": PARTNER_ID,
        "shopid": SHOP_ID,
        "timestamp": str(int(datetime.now(pytz.timezone("Asia/Saigon")).timestamp())),
    }


def build_request(
    uri: str,
    body: dict = {},
) -> tuple[str, dict[str, Any], dict[str, str]]:
    return (
        f"{BASE_URL}/{uri}",
        body,
        {
            "Authorization": sign(f"{BASE_URL}/{uri}", body),
            "Content-type": "application/json",
        },
    )


def request_shopee(
    uri: str,
    body_callback: Callable[[Any], dict],
    result_callback: Callable[[dict], dict],
):
    def request(session: requests.Session, data: Any) -> dict:
        url, body, headers = build_request(uri, build_body(body_callback(data)))
        with session.post(url, json=body, headers=headers) as r:
            r.raise_for_status()
            res = r.json()
            if res.get("error", None):
                raise requests.exceptions.HTTPError(res)
            return result_callback(res)

    return request


get_order_details: Callable[[str], shopee.Order] = request_shopee(
    "orders/detail",
    lambda order_id: {
        "ordersn_list": [order_id],
    },
    lambda res: {
        "ordersn": res["orders"][0]["ordersn"],
        "items": [
            {
                "variation_sku": item["variation_sku"],
                "variation_quantity_purchased": item["variation_quantity_purchased"],
                "variation_original_price": item["variation_original_price"],
                "variation_discounted_price": item["variation_discounted_price"],
            }
            for item in res["orders"][0]["items"]
        ],
    },
)
