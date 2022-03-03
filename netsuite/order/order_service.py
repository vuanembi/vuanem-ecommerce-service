from typing import Callable, Any

from returns.pipeline import flow
from returns.result import Result, ResultE, Success
from returns.iterables import Fold
from returns.pointfree import bind, map_
from google.cloud.firestore import DocumentReference

from netsuite.sales_order import sales_order, sales_order_service
from netsuite.order import order, order_repo
from telegram import telegram, message_service


def ingest(
    creator: Callable[[Any], ResultE[DocumentReference]],
    builder: Callable[[dict], ResultE[sales_order.Order]],
    channel: telegram.Channel,
):
    def _svc(orders: list[dict]) -> ResultE[dict[str, list[dict]]]:
        return Fold.collect_all(
            [
                flow(  # type: ignore
                    order,
                    creator,
                    bind(builder),
                    bind(order_repo.create),
                    map_(message_service.send_new_order(channel)),
                    map_(
                        lambda x: x.get(["source_ref"])  # type: ignore
                        .get("source_ref")
                        .get()
                        .to_dict()
                    ),
                )
                for order in orders
            ],
            Success(()),
        ).map(
            lambda x: {"orders": x}  # type: ignore
        )

    return _svc


def operation(
    validator: Callable[[order.Order], Result[order.Order, str]],
    ops: Callable[[sales_order.Order], ResultE[int]],
    status: str,
):
    def _operation(id: str) -> ResultE[DocumentReference]:
        def __operation(order_doc_ref: DocumentReference) -> ResultE[DocumentReference]:
            return flow(  # type: ignore
                order_doc_ref,
                lambda x: x.get().to_dict(),  # type: ignore
                validator,
                map_(lambda x: x["order"]),  # type: ignore
                bind(ops),
                bind(order_repo.update(order_doc_ref, status)),
            )

        return flow(  # type: ignore
            id,
            order_repo.get,
            bind(__operation),
        )

    return _operation


create = operation(
    order_repo.validate("pending"),
    sales_order_service.create,
    "created",
)
close = operation(
    order_repo.validate("created"),
    sales_order_service.close,
    "closed",
)
