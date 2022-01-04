from typing import Callable, Union, Any

from returns.pipeline import flow
from returns.result import Result, ResultE, Success, safe
from returns.iterables import Fold
from returns.pointfree import bind, lash, map_, alt
from google.cloud import firestore

from netsuite import netsuite, netsuite_repo, prepare_repo, restlet_repo
from telegram import message_service


def build_prepared_order_service(
    items_fn: Callable[[dict], list[dict]],
    item_sku_fn: Callable[[dict], str],
    item_qty_fn: Callable[[dict], int],
    item_amt_fn: Callable[[dict], int],
    item_location: int,
    memo_builder: Callable[[dict], str],
    ecom: netsuite.Ecommerce,
    customer_builder: Callable[
        [dict],
        Union[netsuite.PreparedCustomer, netsuite.Customer],
    ],
):
    def _build(order: dict) -> ResultE[Union[netsuite.PreparedOrder, netsuite.Order]]:
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


def _create_order_from_prepared(chat_id: str):
    def _create(
        prepared_order_doc_ref: firestore.DocumentReference,
    ) -> Result[str, Any]:
        with restlet_repo.netsuite_session() as session:
            return flow(
                prepared_order_doc_ref,
                lambda x: x.get().to_dict(),
                prepare_repo.validate_prepared_order("pending"),
                bind(netsuite_repo.build_sales_order_from_prepared(session)),
                bind(netsuite_repo.create_sales_order(session)),
                map_(lambda x: int(x["id"])),  # type: ignore
                map_(
                    prepare_repo.update_prepared_order_status(
                        prepared_order_doc_ref,
                        "created",
                    )
                ),
                map_(message_service.send_create_order_success(chat_id)),
                alt(message_service.send_create_order_error(chat_id)),
                lash(safe(str)),
            )

    return _create


def create_order_service(chat_id: str, prepared_id: str) -> Result[str, Any]:
    return flow(
        prepared_id,
        prepare_repo.get_prepared_order,
        bind(_create_order_from_prepared(chat_id)),
    )
