import os
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


def build(entry: journal_entry.JournalEntryDraft) -> journal_entry.JournalEntry:
    return {
        "custbody_journal_type2": journal_entry.CUSTBODY_JOURNAL_TYPE2,
        "custbody_cash_flow_code": journal_entry.CUSTBODY_CASH_FLOW_CODE,
        **entry,  # type: ignore
    }


def create(session: OAuth1Session):
    def _create(order: sales_order.Order) -> ResultE[dict[str, str]]:
        return restlet_repo.request(
            session,
            restlet.JournalEntry,
            "POST",
            body={
                **order,
            },
        )

    return _create


def get_url(id: str) -> str:
    return (
        f"https://{os.getenv('ACCOUNT_ID')}.app.netsuite.com/"
        + f"app/accounting/transactions/journal.nl?id={id}"
    )
