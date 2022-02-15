from typing import Callable, Union, Any

from returns.pipeline import flow
from returns.result import Result, ResultE, Success, Failure
from returns.iterables import Fold
from returns.pointfree import bind, lash, map_, alt
from google.cloud.firestore import DocumentReference

from netsuite.restlet import restlet_repo
from netsuite.sales_order import sales_order, sales_order_repo
from netsuite.customer import customer, customer_repo
from netsuite.item import item_repo
from netsuite.order import order, order_repo
from telegram import telegram, message_service



def ingest_orders(
    creator: Callable[[dict], ResultE[dict]],
    builder: Callable[[dict], ResultE[sales_order.Order]],
    channel: telegram.Channel,
):
    def _svc(orders: list[dict]) -> ResultE[dict[str, Any]]:
        return Fold.collect_all(
            [
                flow(  # type: ignore
                    order,
                    creator,
                    bind(builder),
                    bind(order_repo.create),
                    map_(lambda x: x.id),  # type: ignore
                    map_(lambda x: message_service.send_new_order(channel)(order, x)),  # type: ignore
                )
                for order in orders
            ],
            Success(()),
        ).map(lambda x: {"orders": [y[1] for y in x]})

    return _svc


def _create_order_from_prepared(
    order_doc_ref: DocumentReference,
) -> Result[tuple[int, str], tuple[Exception, str]]:
    with restlet_repo.netsuite_session() as session:
        prepared_order = order_doc_ref.get().to_dict()
        return flow(
            prepared_order,
            order_repo.validate("pending"),
            map_(lambda x: x["order"]),  # type: ignore
            bind(sales_order_repo.build(session)),
            bind(netsuite_repo.create_sales_order(session)),
            map_(lambda x: int(x["id"])),  # type: ignore
            map_(
                prepare_repo.update_prepared_order_status(
                    prepared_order_doc_ref,
                    "created",
                )
            ),
            lash(lambda x: Failure((x, prepared_order["order"]["memo"]))),  # type: ignore
        )


def create_order_service(
    prepared_id: str,
) -> Result[tuple[int, str], tuple[Exception, str]]:
    return flow(  # type: ignore
        prepared_id,
        prepare_repo.get_prepared_order,
        alt(lambda x: (x, "")),  # type: ignore
        bind(_create_order_from_prepared),
    )


def _close_order_from_prepared(
    prepared_order_doc_ref: firestore.DocumentReference,
) -> Result[tuple[int, str], tuple[Exception, str, int]]:
    with restlet_repo.netsuite_session() as session:
        prepared_order = prepared_order_doc_ref.get().to_dict()
        return flow(
            prepared_order,
            prepare_repo.validate_prepared_order("created"),
            map_(lambda x: x["transactionId"]),  # type: ignore
            bind(netsuite_repo.close_sales_order(session)),
            map_(lambda x: int(x["id"])),  # type: ignore
            map_(
                prepare_repo.update_prepared_order_status(
                    prepared_order_doc_ref,
                    "closed",
                )
            ),
            lash(
                lambda x: Failure(  # type: ignore
                    (
                        x,
                        prepared_order["order"]["memo"],
                        prepared_order["transactionId"],
                    )
                )
            ),
        )


def close_order_service(
    prepared_id: str,
) -> Result[tuple[int, str], tuple[Exception, str, int]]:
    return flow(  # type: ignore
        prepared_id,
        prepare_repo.get_prepared_order,
        bind(_close_order_from_prepared),
    )
