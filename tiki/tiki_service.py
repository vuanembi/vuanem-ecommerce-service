from typing import Callable

from authlib.integrations.requests_client import OAuth2Session
from returns.result import ResultE, Success
from returns.pointfree import map_
from returns.pipeline import flow
from returns.iterables import Fold
from returns.functions import raise_exception

from tiki import tiki, auth_repo, data_repo
from netsuite import netsuite, netsuite_service, prepare_repo


def auth_service() -> OAuth2Session:
    return auth_repo.get_access_token().map(auth_repo.get_auth_session).unwrap()


prepared_order_builder = netsuite_service.build_prepared_order_service(
    items_fn=lambda x: x["items"],
    item_sku_fn=lambda x: x["product"]["seller_product_code"],
    item_qty_fn=lambda x: x["seller_income_detail"]["item_qty"],
    item_amt_fn=lambda x: x["seller_income_detail"]["sub_total"],
    item_location=netsuite.TIKI_ECOMMERCE["location"],
    ecom=netsuite.TIKI_ECOMMERCE,
    memo_builder=lambda x: f"tiki - {x['code']}",
    customer_builder=lambda x: prepare_repo.build_customer(
        netsuite.TIKI_CUSTOMER,
        x["shipping"]["address"]["phone"],
        x["shipping"]["address"]["full_name"],
    ),
)


def pull_service(session: OAuth2Session) -> ResultE[tiki.EventRes]:
    return (
        data_repo.get_ack_id().bind(data_repo.get_events(session)).lash(raise_exception)
    )


def get_orders_service(
    session: OAuth2Session,
    events: list[tiki.Event],
) -> ResultE[list[tiki.Order]]:
    return Fold.collect_all(
        [
            flow(
                event,
                data_repo.extract_order,
                data_repo.get_order(session),
            )
            for event in events
        ],
        Success(()),
    ).map(list)


def ack_service(ack_id: str) -> Callable[[dict], ResultE[dict]]:
    def _svc(res: dict):
        return flow(
            ack_id,
            data_repo.update_ack_id,
            map_(lambda x: {**res, "ack": x}),  # type: ignore
        )

    return _svc
