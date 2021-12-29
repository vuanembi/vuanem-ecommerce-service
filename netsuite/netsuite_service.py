from typing import Callable, Optional
from returns.pipeline import flow
from returns.result import Result, ResultE, Success, Failure
from returns.iterables import Fold
from returns.pointfree import bind, lash, map_
from returns.functions import tap

from google.cloud import firestore
from netsuite import netsuite, netsuite_repo, prepare_repo, restlet_repo
from telegram import message_service


def build_prepared_order_service(
    items_fn: Callable[[dict], list[dict]],
    item_sku_fn: Callable[[dict], str],
    item_qty_fn: Callable[[dict], int],
    item_amt_fn: Callable[[dict], int],
    memo_builder: Callable[[dict], str],
    ecom: netsuite.Ecommerce,
    customer_builder: Optional[Callable[[dict], netsuite.PreparedCustomer]] = None,
    default_customer: Optional[netsuite.Customer] = None,
):
    def _build(order: dict) -> ResultE[netsuite.PreparedOrder]:
        with restlet_repo.netsuite_session() as session:
            return Fold.collect_all(
                [
                    prepare_repo.build_item(
                        session,
                        item_sku_fn(item),
                        item_qty_fn(item),
                        item_amt_fn(item),
                    )
                    for item in items_fn(order)
                ],
                Success(()),
            ).map(
                lambda x: {
                    "item": list(x),
                    **(
                        customer_builder(order)  # type: ignore
                        if customer_builder
                        else default_customer
                    ),
                    **ecom,
                    **prepare_repo.build_prepared_order_meta(memo_builder(order)),
                }
            )

    return _build


def _create_order_from_prepared(
    prepared_order_doc_ref: firestore.DocumentReference,
) -> Success[Optional[str]]:
    with restlet_repo.netsuite_session() as session:
        return flow(  # type: ignore
            prepared_order_doc_ref,
            lambda x: x.get().to_dict(),
            prepare_repo.validate_prepared_order("pending"),
            bind(netsuite_repo.build_sales_order_from_prepared(session)),
            # bind(netsuite_repo.create_sales_order(session)),
            # map_(lambda x: int(x['id'])),
            # bind(lambda _: Failure(Exception("aaa"))),
            bind(lambda _: Success(1)),  # type: ignore
            tap(
                bind(
                    prepare_repo.update_prepared_order_status(
                        prepared_order_doc_ref, "created"
                    )
                )
            ),
            tap(bind(message_service.send_create_order_success)),  # type: ignore
            tap(lash(message_service.send_create_order_error)),  # type: ignore
            lash(lambda x: Success(str(x))),  # type: ignore
        )


def create_order_service(prepared_id: str) -> Result[Optional[str], Optional[str]]:
    return flow(
        prepared_id,
        prepare_repo.get_prepared_order,
        bind(_create_order_from_prepared),
    )
