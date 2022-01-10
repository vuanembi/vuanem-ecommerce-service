from typing import TypedDict
from enum import Enum


class Restlet(TypedDict):
    script: int
    deploy: int


class SavedSearch(Restlet):
    id: str


SalesOrder: Restlet = {"script": 997, "deploy": 1}
Customer: Restlet = {"script": 1099, "deploy": 1}
InventoryItem: Restlet = {"script": 1101, "deploy": 1}
Analytics: Restlet = {"script": 1098, "deploy": 1}


class Dataset(Enum):
    CouponCode = "custdataset25"


CouponCodeSS: SavedSearch = {"script": 1208, "deploy": 1, "id": "customsearch2131"}
