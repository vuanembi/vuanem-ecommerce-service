from typing import Callable, Union, Any

from returns.pipeline import flow
from returns.result import Result, ResultE, Success, Failure
from returns.iterables import Fold
from returns.pointfree import bind, lash, map_, alt
from google.cloud import firestore

from netsuite.sales_order.sales_order import netsuite_repo, prepare_repo
from netsuite.restlet import restlet_repo
from netsuite.sales_order import sales_order
from telegram import telegram, message_service


def build_prepared_order_service(
    items_fn: Callable[[dict], list[dict]],
    item_sku_fn: Callable[[dict], str],
    item_qty_fn: Callable[[dict], int],
    item_amt_fn: Callable[[dict], int],
    item_location: int,
    memo_builder: Callable[[dict], str],
    ecom: sales_order.Ecommerce,
    customer_builder: Callable[
        [dict],
        Union[sales_order.PreparedCustomer, sales_order.Customer],
    ],
):
    def _build(order: dict) -> ResultE[Union[sales_order.PreparedOrder, sales_order.Order]]:
        with restlet_repo.netsuite_session() as session:
            return Fold.collect_all(
                [
                    prepare_repo.build_item(
                        session,
                        item_sku_fn(item),
                        item_qty_fn(item),
                        item_amt_fn(item),
                        item_location,
                    )
                    for item in items_fn(order)
                ],
                Success(()),
            ).map(
                lambda x: {
                    "item": list(x),
                    **customer_builder(order),  # type: ignore
                    **ecom,
                    **prepare_repo.build_prepared_order_meta(memo_builder(order)),
                }
            )

    return _build


def prepare_orders_service(
    order_persister: Callable[[dict], ResultE[dict]],
    prepared_order_builder: Callable[
        [dict],
        ResultE[Union[sales_order.PreparedOrder, sales_order.Order]],
    ],
    channel: telegram.Channel,
):
    def _svc(orders: list[dict]) -> ResultE[dict[str, Any]]:
        return Fold.collect_all(
            [
                flow(  # type: ignore
                    order,
                    order_persister,
                    bind(prepared_order_builder),
                    bind(prepare_repo.persist_prepared_order),
                    map_(lambda x: x.id),  # type: ignore
                    map_(lambda x: message_service.send_new_order(channel)(order, x)),  # type: ignore
                )
                for order in orders
            ],
            Success(()),
        ).map(lambda x: {"orders": [y[1] for y in x]})

    return _svc


def _create_order_from_prepared(
    prepared_order_doc_ref: firestore.DocumentReference,
) -> Result[tuple[int, str], tuple[Exception, str]]:
    with restlet_repo.netsuite_session() as session:
        prepared_order = prepared_order_doc_ref.get().to_dict()
        return flow(
            prepared_order,
            prepare_repo.validate_prepared_order("pending"),
            map_(lambda x: x["order"]),  # type: ignore
            bind(netsuite_repo.build_sales_order_from_prepared(session)),
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
