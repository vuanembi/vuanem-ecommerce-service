from typing import Any, Optional

from returns.result import Result, ResultE, Success
from returns.pipeline import flow
from returns.pointfree import lash, bind
from returns.methods import cond

from netsuite.restlet import restlet_repo
from netsuite.csv_import import csv_import_repo


def validation_service(
    request_data: dict[str, Any]
) -> Result[dict[str, Any], dict[str, Any]]:
    return cond(
        Result,
        "data" in request_data
        and "id" in request_data["data"]
        and isinstance(request_data["data"]["data"], str),
        request_data["data"],
        request_data["data"],
    )


def csv_import_service(body: dict[str, Any]) -> ResultE[dict[str, Optional[str]]]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            body,
            validation_service,
            bind(csv_import_repo.request(session)),
            lash(lambda _: Success({"data": None})),  # type: ignore
        )
