from typing import Any

from returns.result import Result, ResultE, Success
from returns.pipeline import flow
from returns.pointfree import map_, lash
from returns.methods import cond

from netsuite.restlet import restlet_repo
from netsuite.csv_import import csv_import_repo


def validation_service(
    request_data: dict[str, Any]
) -> Result[dict[str, Any], dict[str, Any]]:
    return cond(
        Result,
        "data" in request_data
        and "id" in request_data
        and isinstance(request_data["data"], str),
        request_data,
        request_data,
    )


def csv_import_service(body: dict[str, Any]) -> ResultE[str]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            body,
            csv_import_repo.request(session),
            map_(lambda x: x["data"]),  # type: ignore
            lash(lambda _: Success("")),  # type: ignore
        )
