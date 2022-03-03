from typing import Any

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, Success
from returns.pipeline import flow
from returns.pointfree import map_, lash

from netsuite.restlet import restlet
from netsuite.query import query_repo


def _query_service(_restlet: restlet.Restlet):
    def _svc(session: OAuth1Session):
        def __svc(body: dict[str, Any]) -> ResultE[list[Any]]:
            return flow(
                body,
                query_repo.request(session, _restlet),
                map_(lambda x: x["data"]),  # type: ignore
                lash(lambda _: Success([])),  # type: ignore
            )

        return __svc

    return _svc


saved_search_service = _query_service(restlet.SavedSearch)
analytics_service = _query_service(restlet.Analytics)
