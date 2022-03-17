from typing import Optional, Callable, Any

import os

from returns.result import ResultE, safe
from authlib.integrations.requests_client import OAuth2Session
from db.firestore import DB
from tiki import tiki


BASE_URL = "https://api.tiki.vn/integration"
QUEUE_CODE = (
    "6cd68367-3bde-4aac-a24e-258bc907d68b"
    if os.getenv("PYTHON_ENV") == "prod"
    else "f0c586e1-fb27-4d73-90bb-bcfe31464dba"
)
TIKI = DB.document("Tiki")


def get_events(session: OAuth2Session):
    @safe
    def _get(ack_id: Optional[str] = None) -> tiki.EventRes:
        with session.post(
            f"{BASE_URL}/v1/queues/{QUEUE_CODE}/events/pull",
            json={
                "ack_id": ack_id,
            },
        ) as r:
            data = r.json()
        return data["ack_id"], data["events"]

    return _get


def extract_order(event: tiki.Event) -> str:
    return event["payload"]["order_code"]


def get_order(session: OAuth2Session) -> Callable[[str], ResultE[tiki.Order]]:
    @safe
    def _get(order_id: str) -> tiki.Order:
        with session.get(
            f"{BASE_URL}/v2/orders/{order_id}",
            params={
                "include": "items.fees",
            },
        ) as r:
            data = r.json()
        return {
            "id": data["id"],
            "code": data["code"],
            "items": [
                {
                    "_fulfillment_type": data.get("fulfillment_type"),
                    "product": {
                        "name": item["product"]["name"],
                        "seller_product_code": item["product"]["seller_product_code"],
                    },
                    "seller_income_detail": {
                        "item_price": item["seller_income_detail"]["item_price"],
                        "item_qty": item["seller_income_detail"]["item_qty"],
                        "sub_total": item["seller_income_detail"]["sub_total"],
                        "discount": {
                            "discount_coupon": {
                                "seller_discount": item["seller_income_detail"][
                                    "discount"
                                ]["discount_coupon"]["seller_discount"]
                            },
                        },
                    },
                }
                for item in data["items"]
            ],
            "shipping": {
                "address": {
                    "full_name": data["shipping"]["address"]["full_name"],
                    "street": data["shipping"]["address"]["street"],
                    "ward": data["shipping"]["address"]["ward"],
                    "district": data["shipping"]["address"]["district"],
                    "phone": data["shipping"]["address"]["phone"],
                },
            },
            "fulfillment_type": data.get("fulfillment_type"),
            "status": data.get("status"),
            "inventory_status": data.get("inventory_status"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    return _get


def get_products(session: OAuth2Session):
    @safe
    def _get():
        def __get(page: int = 1) -> list[dict[str, str]]:
            with session.get(
                f"{BASE_URL}/v2/products",
                params={
                    "limit": 50,
                    "page": page,
                },
            ) as r:
                res = r.json()
            data = res["data"]
            last_page = res["paging"]["last_page"]
            return data + __get(page + 1) if page != last_page else data
        
        return __get()

    return _get


def transform_products(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row.get("id"),
            "sku": row.get("sku"),
            "name": row.get("name"),
            "master_id": row.get("master_id"),
            "master_sku": row.get("master_sku"),
            "super_id": row.get("super_id"),
            "super_sku": row.get("super_sku"),
            "original_sku": row.get("original_sku"),
            "type": row.get("type"),
            "entity_type": row.get("entity_type"),
            "price": row.get("price"),
            "market_price": row.get("market_price"),
            "version": row.get("version"),
            "created_at": row.get("created_at"),
            "created_by": row.get("created_by"),
            "updated_at": row.get("updated_at"),
            "active": row.get("active"),
            "is_hidden": row.get("is_hidden"),
        }
        for row in rows
    ]
