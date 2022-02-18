from typing import TypedDict


CUSTCOL_DELIVER_LOCATION = 50
COMMIT_INVENTORY = 3


class _Item(TypedDict):
    item: int
    quantity: int
    price: int
    amount: int
    commitinventory: int
    location: int
    custcol_deliver_location: int


class Item(_Item, total=False):
    _id: int


class Items(TypedDict):
    item: list[Item]
