from typing import TypedDict


class Restlet(TypedDict):
    script: int
    deploy: int


Record: Restlet = {"script": 1236, "deploy": 1}

SavedSearch: Restlet = {"script": 1208, "deploy": 1}
Analytics: Restlet = {"script": 1098, "deploy": 1}

CSVImportTask: Restlet = {"script": 1233, "deploy": 1}
BankInTransitTask: Restlet = {"script": 1234, "deploy": 1}
VoucherAdjustmentsTask: Restlet = {"script": 1271, "deploy": 1}
