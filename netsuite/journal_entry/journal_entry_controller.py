from typing import Optional
from datetime import date, datetime, timedelta

from flask import Request

from netsuite.journal_entry import bank_in_transit_service

services = {
    "/netsuite/journal_entry/bank_in_transit": bank_in_transit_service.bank_in_transit_service,
}


def journal_entry_controller(request: Request):
    body: Optional[dict[str, str]] = request.get_json()
    if request.path in services:
        return services[request.path](
            datetime.strptime(
                body.get("date", (date.today() - timedelta(days=1)).isoformat()),
                "%Y-%m-%d",
            )
            if body
            else date.today() - timedelta(days=1)
        )
