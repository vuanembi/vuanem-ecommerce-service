from datetime import date, timedelta

from returns.result import ResultE, Success, Failure
from returns.pipeline import flow
from returns.pointfree import map_, bind
from returns.curry import curry

from netsuite.restlet import restlet_repo
from netsuite.location import location
from netsuite.journal_entry import journal_entry_repo
from netsuite.query import query_service
from netsuite.query.saved_search import saved_search
from mail import sendgrid_repo, template_repo


def bank_in_transit_service(
    _date: date = date.today() - timedelta(days=1),
) -> ResultE[str]:
    @curry
    def _send_email(entries: list[dict[str, str]], je_id: str) -> str:
        fields = [
            "tranid",
            "trandate",
            "amount",
            "memo",
        ]
        sendgrid_repo.send_email(
            to=[
                "bi@vuanem.com",
                "doisoat.tckt@vuanem.com.vn",
            ],
            subject=f"VNBI Bank In Transit {_date.isoformat()}",
            content=[
                {
                    "type": "text/html",
                    "value": template_repo.get_template(
                        "netsuite/journal_entry/bank_in_transit.html"
                    ).render(
                        link=journal_entry_repo.get_url(je_id),
                        headers=fields,
                        entries=[
                            {field: entry[field] for field in fields}
                            for entry in entries
                        ],
                    ),
                }
            ],
        )
        return je_id

    with restlet_repo.netsuite_session() as session:
        entries = flow(
            {
                "id": saved_search.SavedSearch.BankInTransit.value,
                "filterExp": [
                    ["trandate", "WITHIN", _date.isoformat(), _date.isoformat()],
                    "AND",
                    ["account.custrecord_intransit_bank_at_store", "IS", "T"],
                    "AND",
                    ["account.number", "CONTAINS", "113343"],
                    "AND",
                    ["type", "ANYOF", "CustDep", "CustPymt"],
                ],
            },
            query_service.saved_search_service(session),
        )

        je_id = flow(
            entries,
            bind(lambda x: Success(x) if x else Failure(x)),  # type: ignore
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
        return (
            flow(
                Success(_send_email),
                entries.apply,
                je_id.apply,
            )
            .map(lambda x: {"result": x})
            .lash(lambda _: Success({"result": None}))
        )
