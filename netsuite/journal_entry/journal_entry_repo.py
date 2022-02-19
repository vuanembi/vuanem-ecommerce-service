from datetime import date, timedelta

from dateutil import rrule
from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.sales_order import sales_order
from netsuite.journal_entry import journal_entry
from netsuite.restlet import restlet, restlet_repo


def add_working_days(_date: date, days: int = 1) -> date:
    return rrule.rrule(
        rrule.DAILY,
        byweekday=(
            rrule.MO,
            rrule.TU,
            rrule.WE,
            rrule.TH,
            rrule.FR,
        ),
        dtstart=_date + timedelta(days=1),
        count=days,
    )[-1].date()


def build_bank_in_transit_lines(entries: list[dict]) -> list[journal_entry.Line]:
    return [
        {
            "line_type": "debit",
            "account": journal_entry.BANK_IN_TRANSIT_DR_ACCOUNT,
            "entity": None,
            "location": journal_entry.BANK_IN_TRANSIT_DR_LOCATION,
            "amount": int(sum([float(entry["amount"]) for entry in entries])),
        },
        *[  # type: ignore
            {
                "line_type": "credit",
                "account": journal_entry.BANK_IN_TRANSIT_CR_ACCOUNT,
                "entity": int(entry["internalid"]),
                "location": int(entry["custbody_in_charge_location"]),
                "amount": int(float(entry["amount"])),
            }
            for entry in entries
        ],
    ]


def build(entry: journal_entry.JournalEntryDraft) -> journal_entry.JournalEntry:
    return {
        "custbody_journal_type2": journal_entry.CUSTBODY_JOURNAL_TYPE2,
        "custbody_cash_flow_code": journal_entry.CUSTBODY_CASH_FLOW_CODE,
        **entry,  # type: ignore
    }


def create(session: OAuth1Session):
    def _create(order: sales_order.Order) -> ResultE[dict]:
        return restlet_repo.request(
            session,
            restlet.JournalEntry,
            "POST",
            body={
                **order,
            },
        )

    return _create
