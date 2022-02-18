from datetime import date

from returns.pipeline import flow
from returns.pointfree import map_

from netsuite.analytics import analytics_repo
from netsuite.restlet import restlet, restlet_repo


def bank_in_transit(start: date, end: date):
    with restlet_repo.netsuite_session() as session:
        return flow(
            tuple([i.isoformat() for i in [start, end]]),
            lambda x: {
                "id": restlet.SavedSearchID.BankInTransit.value,
                "filterExp": [
                    ["trandate", "WITHIN", x[0], x[1]],
                    "AND",
                    ["account.custrecord_intransit_bank_at_store", "IS", "T"],
                    "AND",
                    ["account.number", "CONTAINS", "113343"],
                    "AND",
                    ["type", "ANYOF", "CustDep", "CustPymt"],
                ],
            },
            analytics_repo.request(session, restlet.SavedSearch),
            map_(lambda x: x["data"]),  # type: ignore
        )
