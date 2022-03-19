from typing import Any

from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.restlet import restlet, restlet_repo
from netsuite.csv_import import csv_import


def request(session: OAuth1Session):
    def _request(body: dict[str, Any]) -> ResultE[csv_import.CSVTaskResponse]:
        return restlet_repo.request(  # type: ignore
            session,
            restlet.CSVImportTask,
            "POST",
            body=body,
        )

    return _request
