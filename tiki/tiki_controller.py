from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE

from tiki import tiki, tiki_service, data_repo
from netsuite import netsuite_service
from telegram import telegram


def service_factory(session: OAuth2Session):
    def _svc(event_res: tiki.EventRes) -> ResultE[dict]:
        ack_id, events = event_res
        return (
            tiki_service.get_orders_service(session, events)
            .bind(
                netsuite_service.prepare_orders_service(
                    data_repo.persist_tiki_order,  # type: ignore
                    tiki_service.prepared_order_builder,
                    telegram.TIKI_CHANNEL,
                )
            )
            .bind(tiki_service.ack_service(ack_id))
        )

    return _svc


def tiki_controller(request_data: dict) -> dict:
    with tiki_service.auth_service() as session:
        return (
            tiki_service.pull_service(session)
            .bind(service_factory(session))
            .map(lambda x: {"controller": "tiki", "results": x})
        ).unwrap()
