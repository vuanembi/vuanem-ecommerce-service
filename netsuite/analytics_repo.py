from typing import Any

from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite import restlet, restlet_repo


def post_analytics(session: OAuth1Session):
    def _post(body: dict) -> ResultE[dict[str, Any]]:
        return restlet_repo.request(
            session,
            restlet.Analytics,
            "POST",
            body=body,
        )

    return _post


def get_saved_search(saved_search: restlet.SavedSearch):
    def _get(session: OAuth1Session):
        def __get(params: dict) -> ResultE[dict[str, Any]]:
            return restlet_repo.request(
                session,
                saved_search,
                "GET",
                params=params,
            )

        return __get

    return _get
