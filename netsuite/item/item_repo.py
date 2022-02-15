from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.item import item
from netsuite.restlet import restlet, restlet_repo


def _map_sku(session: OAuth1Session, sku: str) -> ResultE[str]:
    return restlet_repo.request(
        session,
        restlet.InventoryItem,
        "GET",
        params={"itemid": sku},
    ).map(lambda x: x["id"])


def build(
    session: OAuth1Session,
    sku: str,
    qty: int,
    amt: int,
    location: int,
) -> ResultE[item.Item]:
    return _map_sku(session, sku).map(
        lambda x: {
            "item": int(x),
            "quantity": qty,
            "price": -1,
            "amount": int(amt / 1.08),
            "commitinventory": item.COMMIT_INVENTORY,
            "location": location,
            # ! hardcoded
            "custcol_deliver_location": item.CUSTCOL_DELIVER_LOCATION,
        }
    )
