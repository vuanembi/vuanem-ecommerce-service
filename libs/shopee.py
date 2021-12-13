from typing import Callable, Any
import os
import hmac
import hashlib
import json
from datetime import datetime

import requests

from models.ecommerce import shopee

BASE_URL = (
    "https://partner.shopeemobile.com/api/v1"
    if os.getenv("PYTHON_ENV") == "prod"
    else "https://partner.test-stable.shopeemobile.com/api/v1"
)
PARTNER_ID = "1004299" if os.getenv("PYTHON_ENV") == "prod" else "1004299"
SHOP_ID = "29042" if os.getenv("PYTHON_ENV") == "prod" else "29042"


def sign(url: str, body: dict) -> str:
    return hmac.new(
        os.getenv("SHOPEE_SECRET_KEY", "").encode(),
        msg=f"{url}|{json.dumps(body)}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def build_request(
    uri: str,
    body: dict = {},
) -> tuple[str, dict[str, Any], dict[str, str]]:
    return (
        f"{BASE_URL}/{uri}",
        {
            **body,
            "partner_id": PARTNER_ID,
            "shopid": SHOP_ID,
            "timestamp": int(datetime.utcnow().timestamp()),
        },
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
        url, body, headers = build_request(uri, body_callback(data))
        with session.post(url, json=body, headers=headers) as r:
            return result_callback(r.json())

    return request


get_order_details: Callable[[str], shopee.Order] = request_shopee(
    "/orders/detail",
    lambda order_id: {
        "ordersn_list": [order_id],
    },
    lambda res: {
        "ordersn": res["orders"][0],
        "items": [
            {
                "variation_sku": item["variation_sku"],
                "variation_quantity_purchased": item["variation_quantity_purchased"],
                "variation_original_price": item["variation_original_price"],
                "variation_discounted_price": item["variation_discounted_price"],
            }
            for item in res["orders"][0]
        ],
    },
)
