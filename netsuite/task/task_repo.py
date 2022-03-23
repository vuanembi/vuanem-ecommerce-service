from typing import Any

from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.restlet import restlet, restlet_repo


def request(session: OAuth1Session, _restlet: restlet.Restlet):
    def _request(body: dict[str, Any]) -> ResultE[dict[str, Any]]:
        return restlet_repo.request(
            session,
            _restlet,
            "POST",
            body=body,
        )

    return _request
