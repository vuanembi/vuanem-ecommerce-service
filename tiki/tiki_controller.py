from returns.functions import raise_exception

from tiki.tiki_service import auth_service, pull_service, events_service, ack_service


def tiki_controller(request_data: dict) -> dict:
    with auth_service() as session:
        ack_id, events = pull_service(session)
        return {
            "controller": "tiki",
            "results": events.bind(events_service(session))
            .bind(ack_id.bind(ack_service)) # type: ignore
            .lash(raise_exception)
            .unwrap(),
        }
