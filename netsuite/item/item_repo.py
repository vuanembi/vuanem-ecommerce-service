import random
from datetime import datetime

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, safe
from returns.pipeline import flow
from returns.pointfree import bind

from netsuite.item import item
from netsuite.query import query_service
from netsuite.query.saved_search import saved_search


def _map_sku(session: OAuth1Session, sku: str) -> ResultE[int]:
    return flow(
        {
            "id": saved_search.SavedSearch.InventoryItem.value,
            "filterExp": [
                ["type", "ANYOF", "InvtPart"],
                "AND",
                ["externalid", "ANYOF", sku],
            ],
        },
        query_service.saved_search_service(session),
        bind(safe(lambda x: x[0]["internalid"])),
    )


def random_item_id() -> int:
    # ! TODO frontend parseInt(Date.now() * Math.random())
    return int(datetime.now().timestamp() * 1000 * random.random())


def build(
    session: OAuth1Session,
    sku: str,
    qty: int,
    amt: int,
    location: int,
) -> ResultE[item.Item]:
    return _map_sku(session, sku).map(
        lambda x: {
            "_id": random_item_id(),
            "item": int(x),
            "quantity": qty,
            "price": -1,
            "amount": int(amt / 1.08),
            "commitinventory": item.COMMIT_INVENTORY,
            "location": location,
            "custcol_deliver_location": item.CUSTCOL_DELIVER_LOCATION,
        }
    )
