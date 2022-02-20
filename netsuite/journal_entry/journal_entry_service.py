from datetime import date

from returns.result import ResultE
from returns.pipeline import flow
from returns.pointfree import map_, bind

from netsuite.restlet import restlet_repo
from netsuite.location import location
from netsuite.journal_entry import journal_entry_repo
from netsuite.query import query_service
from netsuite.query.saved_search import saved_search


def bank_in_transit_service(_date: date) -> ResultE[str]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            {
                "id": saved_search.SavedSearch.BankInTransit.value,
                "filterExp": [
                    ["trandate", "WITHIN", _date, _date],
                    "AND",
                    ["account.custrecord_intransit_bank_at_store", "IS", "T"],
                    "AND",
                    ["account.number", "CONTAINS", "113343"],
                    "AND",
                    ["type", "ANYOF", "CustDep", "CustPymt"],
                ],
            },
            query_service.saved_search_service(session),
            map_(journal_entry_repo.build_bank_in_transit_lines),
            map_(  # type: ignore
                lambda x: {
                    "custbody_ref_transaction": None,
                    "subsidiary": location.SUBSIDIARY,
                    "memo": f"VNBI - {_date.isoformat()}",
                    "trandate": journal_entry_repo.add_working_days(_date).isoformat(),
                    "lines": x,
                }
            ),
            map_(journal_entry_repo.build),
            bind(journal_entry_repo.create(session)),
            map_(lambda x: x["id"]),  # type: ignore
        )
