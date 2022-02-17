from typing import Any

from flask import Request
from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE

from tiki import tiki, tiki_service, order_repo
from netsuite.order import order_service
from telegram import telegram


def service_factory(session: OAuth2Session):
    def _svc(event_res: tiki.EventRes) -> ResultE[dict]:
        ack_id, events = event_res
        return (
            tiki_service.get_orders_service(session, events)
            .bind(
                order_service.ingest(
                    order_repo.create,  # type: ignore
                    tiki_service.builder,
                    telegram.TIKI_CHANNEL
                )
            )
            .bind(tiki_service.ack_service(ack_id))
        )

    return _svc


def tiki_controller(request: Request) -> dict[str, Any]:
    with tiki_service.auth_service() as session:
        return (
            tiki_service.pull_service(session)
            .bind(service_factory(session))
            .map(lambda x: {"controller": "tiki", "results": x})
        ).unwrap()
