import requests
from returns.result import Success
from returns.functions import raise_exception

from tiki.TikiService import auth_service, pull_service, events_service, ack_service


def tiki_controller(request_data: dict) -> dict:
    with requests.Session() as session:
        (
            auth_service(session)
            .bind(lambda x: Success(session.headers.update(x)))
            .lash(raise_exception)
        )
        ack_id, events = pull_service(session)
        return {
            "controller": "tiki",
            "results": events.bind(events_service(session))
            .bind(ack_service(ack_id))
            .lash(raise_exception)
            .unwrap(),
        }
