from flask import Request

from netsuite.journal_entry import journal_entry
from netsuite.journal_entry.journal_entry_service import bank_in_transit_service

services = {
    "/netsuite/journal_entry/bank_in_transit/warehouse": bank_in_transit_service(
        journal_entry.BankInTransitWarehouse
    ),
    "/netsuite/journal_entry/bank_in_transit/online": bank_in_transit_service(
        journal_entry.BankInTransitOnline
    ),
}


def journal_entry_controller(request: Request):
    if request.path in services:
        return services[request.path](request.get_json()).unwrap()
