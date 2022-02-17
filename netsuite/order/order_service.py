from typing import Callable

from returns.pipeline import flow
from returns.result import Result, ResultE, Success
from returns.iterables import Fold
from returns.pointfree import bind, map_, alt
from google.cloud.firestore import DocumentReference

from netsuite.sales_order import sales_order, sales_order_service
from netsuite.order import order_repo
from telegram import telegram, message_service


def ingest(
    creator: Callable[[dict], ResultE[DocumentReference]],
    builder: Callable[[dict], ResultE[sales_order.Order]],
    channel: telegram.Channel,
):
    def _svc(orders: list[dict]) -> ResultE[dict[str, list[str]]]:
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


def operation(ops: Callable[[sales_order.Order], ResultE[int]], status: str):
    def _operation(id: str) -> Result[tuple[int, str], tuple[Exception, str]]:
        def __operation(order_doc_ref: DocumentReference) -> ResultE[tuple[int, str]]:
            return flow(
                order_doc_ref,
                map_(lambda x: x.get().to_dict()),  # type: ignore
                map_(lambda x: x["order"]),  # type: ignore
                bind(ops),
                bind(order_repo.update(order_doc_ref, status)),
                alt(lambda x: (x, "")),  # type: ignore
            )

        return flow(  # type: ignore
            id,
            order_repo.get,
            map_(__operation),
        )

    return _operation


create = operation(sales_order_service.create, "created")
close = operation(sales_order_service.close, "closed")
