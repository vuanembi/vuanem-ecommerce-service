from typing import Optional, Any
from datetime import date, datetime, timedelta
from itertools import groupby

from returns.result import ResultE, Success, Failure
from returns.pipeline import flow
from returns.pointfree import map_, bind
from returns.curry import curry
from returns.iterables import Fold
from requests_oauthlib import OAuth1Session

from netsuite.restlet import restlet_repo
from netsuite.location import location
from netsuite.journal_entry import journal_entry, journal_entry_repo
from netsuite.query import query_service
from mail import sendgrid_repo, template_repo


@curry
def _send_email_service(
    name: str,
    entries: list[dict[str, str]],
    _date: date,
    je_ids: list[str],
) -> list[str]:
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
        subject=f"VNBI Bank In Transit {name} {_date.isoformat()}",
        content=[
            {
                "type": "text/html",
                "value": template_repo.get_template(
                    "netsuite/journal_entry/bank_in_transit.html"
                ).render(
                    links=[journal_entry_repo.get_url(i) for i in je_ids],
                    headers=fields,
                    entries=[
                        {field: entry[field] for field in fields} for entry in entries
                    ],
                ),
            }
        ],
    )
    return je_ids


def get_entries_service(
    session: OAuth1Session,
    options: journal_entry.BankInTransitOptions,
    _date: date,
) -> ResultE[list[tuple[int, list[dict]]]]:
    return flow(
        {
            "id": options.saved_search,
            "filterExp": [
                ["trandate", "WITHIN", _date.isoformat(), _date.isoformat()],
                "AND",
                ["account.custrecord_intransit_bank_at_store", "IS", "T"],
                "AND",
                sum(
                    [
                        [i, "OR"]
                        for i in [
                            ["account.number", "CONTAINS", i]
                            for i in options.account_filter
                        ]
                    ],
                    [],
                )[:-1],
                "AND",
                ["type", "ANYOF", "CustDep", "CustPymt"],
            ],
        },
        query_service.saved_search_service(session),
        bind(lambda x: Success(x) if x else Failure(x)),  # type: ignore
        map_(  # type: ignore
            lambda entries: [(k, v) for k, v in groupby(entries, options.group_key_fn)]
        ),
    )


@curry
def create_journal_entry_service(
    session: OAuth1Session,
    options: journal_entry.BankInTransitOptions,
    _date: date,
    entries_group: list[tuple[str, Any]],
) -> ResultE[str]:
    def _create(entries: list[dict]):
        x = flow(  # type: ignore
            entries,
            options.build_fn,
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
            # bind(journal_entry_repo.create(session)),
            # map_(lambda x: [x["id"]]),  # type: ignore
        )
        x

    return Fold.collect_all(
        [_create(entries_group[1]) for entries_group in entries_group],
        Success(()),
    )


def bank_in_transit_service(options: journal_entry.BankInTransitOptions):
    def _svc(body: Optional[dict[str, str]]) -> ResultE[dict[str, Any]]:
        _date = (
            datetime.strptime(body["date"], "%Y-%m-%d").date()
            if body and "date" in body and body["date"]
            else date.today() - timedelta(days=1)
        )

        with restlet_repo.netsuite_session() as session:
            entries_groups: ResultE[list[tuple[str, Any]]] = flow(
                {
                    "id": options.saved_search,
                    "filterExp": [
                        ["trandate", "WITHIN", _date.isoformat(), _date.isoformat()],
                        "AND",
                        ["account.custrecord_intransit_bank_at_store", "IS", "T"],
                        "AND",
                        sum(
                            [
                                [i, "OR"]
                                for i in [
                                    ["account.number", "CONTAINS", i]
                                    for i in options.account_filter
                                ]
                            ],
                            [],
                        )[:-1],
                        "AND",
                        ["type", "ANYOF", "CustDep", "CustPymt"],
                    ],
                },
                query_service.saved_search_service(session),
                bind(lambda x: Success(x) if x else Failure(x)),  # type: ignore
                map_(  # type: ignore
                    lambda entries: [
                        (k, v) for k, v in groupby(entries, options.group_key_fn)
                    ]
                ),
            )

            je_ids = entries_groups.map(
                create_journal_entry_service(
                    session,
                    options,
                    _date,
                )
            )
            return (
                flow(  # type: ignore
                    Success(_send_email_service),
                    entries_groups.map(
                        lambda e: [i for j in [f for _, f in e] for i in j]
                    ).apply,
                    je_ids.apply,
                )
                .map(lambda x: {"result": x})
                .lash(lambda _: Success({"result": None}))  # type: ignore
            )

    return _svc
