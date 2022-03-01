from typing import Any

from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.restlet import restlet, restlet_repo
from netsuite.query import query


def request(session: OAuth1Session, _restlet: restlet.Restlet):
    def _request(body: dict[str, Any]) -> ResultE[query.QueryResponse]:
        return restlet_repo.request(  # type: ignore
            session,
            _restlet,
            "POST",
            body=body,
        )

    return _request
