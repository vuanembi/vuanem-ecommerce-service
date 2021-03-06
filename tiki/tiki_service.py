from typing import Callable

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success
from returns.pointfree import map_, bind
from returns.pipeline import flow
from returns.iterables import Fold
from returns.functions import raise_exception

from netsuite.order import order_service
from tiki import tiki, tiki_repo, auth_repo, event_repo, order_repo, seller
from telegram import message_service

from db import bigquery


def auth_service() -> OAuth2Session:
    return auth_repo.get_access_token().map(auth_repo.get_auth_session).unwrap()


def _pull_service(session: OAuth2Session) -> ResultE[tiki.EventRes]:
    return (
        event_repo.get_ack_id()
        .bind(tiki_repo.get_events(session))
        .lash(raise_exception)
    )


def _get_orders_service(
    session: OAuth2Session,
    events: list[tiki.Event],
) -> ResultE[list[tiki.Order]]:
    return Fold.collect_all(  # type: ignore
        [
            flow(
                event,
                tiki_repo.extract_order,
                tiki_repo.get_order(session),
            )
            for event in events
        ],
        Success(()),
    ).map(list)


def _ack_service(ack_id: str) -> Callable[[dict], ResultE[dict]]:
    def _svc(res: dict):
        return flow(
            ack_id,
            event_repo.update_ack_id,
            map_(lambda x: {**res, "ack": x}),  # type: ignore
        )

    return _svc


def ingest_orders_service():
    def _ingest(session: OAuth2Session):
        def __ingest(event_res: tiki.EventRes) -> ResultE[dict]:
            ack_id, events = event_res
            return (
                _get_orders_service(session, events)
                .bind(
                    order_service.ingest(
                        order_repo.create,  # type: ignore
                        seller.TIKI.order_builder,  # type: ignore
                        seller.TIKI.name,
                        seller.TIKI.chat_id,
                    )
                )
                .bind(_ack_service(ack_id))
            )

        return __ingest

    with auth_service() as session:
        return _pull_service(session).bind(_ingest(session))


def get_products_service() -> ResultE[int]:
    with auth_service() as session:
        return flow(
            tiki_repo.get_products(session)(),
            map_(tiki_repo.transform_products),
            bind(
                bigquery.load(
                    "IP_3rdPartyEcommerce",
                    "Tiki_Products",
                    tiki.ProductsSchema,  # type: ignore
                )
            ),
        )


def alert_products_service() -> ResultE[int]:
    with auth_service() as session:
        return flow(
            tiki_repo.get_products(session)(),
            map_(tiki_repo.transform_products),
            map_(
                lambda products: [
                    {
                        "name": product["name"],
                        "price": product["price"],
                        "market_price": product["market_price"],
                    }
                    for product in products  # type: ignore
                    if product["price"] == product["market_price"]
                    and product["price"] != 0
                    and product["active"] == "1"
                ]
            ),  # type: ignore
            map_(message_service.send_products_alert("-688466638")),
        )
