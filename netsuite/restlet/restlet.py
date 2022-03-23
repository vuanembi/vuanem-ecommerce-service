from typing import TypedDict


class Restlet(TypedDict):
    script: int
    deploy: int


# SalesOrder: Restlet = {"script": 997, "deploy": 1}
# Customer: Restlet = {"script": 1099, "deploy": 1}
Record: Restlet = {"script": 1236, "deploy": 1}

SavedSearch: Restlet = {"script": 1208, "deploy": 1}
Analytics: Restlet = {"script": 1098, "deploy": 1}

CSVImportTask: Restlet = {"script": 1233, "deploy": 1}
BankInTransitTask: Restlet = {"script": 1234, "deploy": 1}
