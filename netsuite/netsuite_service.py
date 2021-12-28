from typing import Callable, Optional
from returns.pipeline import flow
from returns.result import ResultE, Success, Failure
from returns.iterables import Fold
from returns.pointfree import bind, lash
from returns.functions import tap

from netsuite import netsuite, netsuite_repo, prepare_repo, restlet_repo
from telegram import message_service


def build_prepared_order_service(
    items_fn: Callable[[dict], list[dict]],
    item_sku_fn: Callable[[dict], dict],
    item_qty_fn: Callable[[dict], dict],
    item_amt_fn: Callable[[dict], dict],
    memo_builder: Callable[[dict], str],
    ecom: netsuite.Ecommerce,
    customer_builder: Optional[Callable[[dict], dict]] = None,
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
                    "items": list(x),
                    **(
                        customer_builder(order)
                        if customer_builder
                        else default_customer
                    ),
                    **ecom,
                    **prepare_repo.build_prepared_order_meta(memo_builder(order)),
                }
            )

    return _build

def create_order_service(prepared_id: str) -> ResultE[Optional[str]]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            prepared_id,
            prepare_repo.get_prepared_order,
            bind(lambda x: Success(x.to_dict())),
            bind(prepare_repo.validate_prepared_order("pending")),
            bind(netsuite_repo.build_sales_order_from_prepared(session)),
            bind(netsuite_repo.create_sales_order(session)),
            # bind(lambda _: Failure(Exception('aaa'))),
            # bind(lambda _: Success("1")),
            tap(bind(message_service.send_create_order_success)),
            tap(lash(message_service.send_create_order_error)),
            lash(lambda _: Success(None))
        )
