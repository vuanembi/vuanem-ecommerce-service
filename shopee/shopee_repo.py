from typing import Any, Callable, Union
import os
import time
import hashlib
import hmac

import requests

from db.firestore import DB

BASE_URL = "https://partner.shopeemobile.com"
API_PATH = "api/v2"
PARTNER_ID = 2002943
SHOP_ID = 179124960

SHOPEE = DB.document("Shopee")


def sign_params(
    uri: str,
    access_token: str,
    shop_id: Union[int, str],
) -> dict[str, Any]:
    ts = int(time.time())
    return {
        "partner_id": PARTNER_ID,
        "timestamp": ts,
        **({"shop_id": shop_id} if shop_id else {}),
        "sign": hmac.new(
            os.getenv("SHOPEE_API_KEY", "").encode("utf-8"),
            f"{PARTNER_ID}/{API_PATH}/{uri}{ts}{access_token}{shop_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest(),
    }


def build_shopee_request(
    access_token: str = "",
    shop_id_position: str = "body",
) -> Callable[[str, dict[str, Union[int, str]]], requests.PreparedRequest]:
    def _build(uri: str, body: dict[str, Union[int, str]]) -> requests.PreparedRequest:
        return requests.Request(
            "POST",
            url=f"{BASE_URL}/{API_PATH}/{uri}",
            params=sign_params(
                uri,
                access_token,
                SHOP_ID if shop_id_position == "query" else "",
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
            headers={"Content-Type": "application/json"},
        ).prepare()

    return _build


# get_order_details: Callable[[str], shopee.Order] = request_shopee(
#     "orders/detail",
#     lambda order_id: {
#         "ordersn_list": [order_id],
#     },
#     lambda res: {
#         "ordersn": res["orders"][0]["ordersn"],
#         "items": [
#             {
#                 "variation_sku": item["variation_sku"],
#                 "variation_quantity_purchased": item["variation_quantity_purchased"],
#                 "variation_original_price": item["variation_original_price"],
#                 "variation_discounted_price": item["variation_discounted_price"],
#             }
#             for item in res["orders"][0]["items"]
#         ],
#     },
# )
