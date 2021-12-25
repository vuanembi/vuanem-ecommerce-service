from typing import TypedDict


class Restlet(TypedDict):
    script: int
    deploy: int


SalesOrder: Restlet = {"script": 997, "deploy": 1}
Customer: Restlet = {"script": 1099, "deploy": 1}
InventoryItem: Restlet = {"script": 1101, "deploy": 1}
