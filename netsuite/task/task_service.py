from typing import Any, Optional
from datetime import datetime, date, timedelta
import pytz

from returns.result import Result, ResultE, Success
from returns.pipeline import flow
from returns.pointfree import lash, bind, map_
from returns.iterables import Fold
from returns.methods import cond

from netsuite.restlet import restlet, restlet_repo
from netsuite.task import task_repo

TIMEZONE = pytz.timezone("Asia/Ho_Chi_Minh")


def validation_service(
    request_data: dict[str, Any]
) -> Result[dict[str, Any], dict[str, Any]]:
    return cond(  # type: ignore
        Result,
        "data" in request_data
        and "id" in request_data["data"]
        and isinstance(request_data["data"]["data"], str),
        request_data["data"],
        request_data["data"],
    )


def _parse_date_range(body: dict[str, Any], default_: date) -> list[str]:
    if body and "date" in body and body["date"]:
        return [datetime.strptime(body["date"], "%Y-%m-%d").date().isoformat()]

    weekday = default_.weekday()
    if weekday in (4, 5):
        return []
    elif weekday == 6:
        return [
            i.isoformat()
            for i in [
                default_,
                default_ - timedelta(days=1),
                default_ - timedelta(days=2),
            ]
        ]
    else:
        return [default_.isoformat()]


def _parse_date(body: dict[str, Any], default_: date) -> str:
    return (
        datetime.strptime(body["date"], "%Y-%m-%d").date().isoformat()
        if body and "date" in body and body["date"]
        else default_.isoformat()
    )


def csv_import_service(body: dict[str, Any]) -> ResultE[dict[str, Optional[str]]]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            body,
            validation_service,
            bind(task_repo.request(session, restlet.CSVImportTask)),
            lash(lambda _: Success({"data": None})),  # type: ignore
        )


def bank_in_transit_service(body: dict[str, Any]) -> ResultE[dict[str, Any]]:
    dates = _parse_date_range(body, date.today() - timedelta(days=1))

    with restlet_repo.netsuite_session() as session:
        return (
            Fold.collect_all(
                [
                    flow(
                        {"date": _date},
                        task_repo.request(session, restlet.BankInTransitTask),
                        map_(lambda x: {"data": x}),  # type: ignore
                        lash(lambda _: Success({"data": None})),  # type: ignore
                    )
                    for _date in dates
                ],
                Success(()),
            )
            .map(lambda x: {"data": x})
            .lash(lambda _: Success({"data": None}))
        )


def voucher_adjustments_service(body: dict[str, Any]) -> ResultE[dict[str, Any]]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            {"date": _parse_date(body, datetime.now(TIMEZONE).date())},
            task_repo.request(session, restlet.VoucherAdjustmentsTask),
            map_(lambda x: {"data": x}),  # type: ignore
            lash(lambda _: Success({"data": None})),
        )  # type: ignore
