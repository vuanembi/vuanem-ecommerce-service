import requests
from returns.pipeline import flow
from returns.pointfree import bind

from tiki.TikiService import authenticate, get_events, events_service, ack_service


def tiki_controller(request_data: dict) -> dict:
    with requests.Session() as session:
        session.headers.update(authenticate(session))
        ack_id, events = get_events(session)
        return {
            "controller": "tiki",
            "results": flow(  # type: ignore
                events,
                bind(events_service(session)),
                bind(ack_service(ack_id)),
            ).unwrap(),
        }
