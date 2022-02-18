from requests_oauthlib import OAuth1Session
from returns.result import ResultE

from netsuite.restlet import restlet, restlet_repo


def request(session: OAuth1Session, _restlet: restlet.Restlet):
    def _request(body: dict) -> ResultE[restlet.AnalyticsResponse]:
        return restlet_repo.request(  # type: ignore
            session,
            _restlet,
            "POST",
            body=body,
        )

    return _request
