from typing import Optional
from datetime import datetime, tzinfo

import dateparser
import pytz
import requests
from returns.result import safe
from google.cloud import firestore

from db.firestore import DB
from lazada import lazada, lazada_repo

LAZADA = DB.document("Lazada")

ORDER = LAZADA.collection("Order")
PAGE_LIMIT = 100


def parse_timestamp(x: str) -> Optional[datetime]:
    parsed = dateparser.parse(x)
    return parsed.astimezone(pytz.utc).replace(tzinfo=None) if parsed else None


def get_auth_builder(token: lazada.AccessToken) -> lazada.AuthBuilder:
    return lazada_repo.build_lazada_request("https://api.lazada.vn/rest", token)


def get_orders(session: requests.Session, auth_builder: lazada.AuthBuilder):
    @safe
    def _get(created_after: datetime):
        def __get(offset: int = 0):
            with session.send(
                auth_builder(
                    "/orders/get",
                    {
                        "created_after": created_after.isoformat(timespec="seconds"),
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
                }
                for order in res["data"]["orders"]
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


@safe
def persist_order(order):
    doc_ref = ORDER.document()
    doc_ref.create({"order": order, "updated_at": firestore.SERVER_TIMESTAMP})
    return order


@safe
def get_max_created_at() -> datetime:
    return (
        LAZADA.get(["state.max_created_at"])
        .get("state.max_created_at")
        .replace(tzinfo=None)
    )


@safe
def persist_max_created_at(orders: list[lazada.OrderItems]) -> list[lazada.OrderItems]:
    LAZADA.set(
        {
            "state": {
                "max_created_at": max([order["created_at"] for order in orders]),
            },
        },
        merge=True,
    )
    return orders
