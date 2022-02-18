from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.sales_order import sales_order
from netsuite.journal_entry import journal_entry
from netsuite.restlet import restlet, restlet_repo


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
            restlet.SalesOrder,
            "POST",
            body={
                **order,
            },
        )

    return _create
