from typing import Callable

from returns.pipeline import flow
from returns.result import ResultE, Success
from returns.iterables import Fold
from returns.pointfree import bind, map_

from netsuite.restlet import restlet_repo
from netsuite.sales_order import sales_order, sales_order_repo
from netsuite.customer import customer
from netsuite.item import item_repo


def build(
    items_fn: Callable[[dict], list[dict]],
    item_sku_fn: Callable[[dict], str],
    item_qty_fn: Callable[[dict], int],
    item_amt_fn: Callable[[dict], int],
    item_location: int,
    memo_builder: Callable[[dict], str],
    ecom: sales_order.Ecommerce,
    customer_builder: Callable[[dict], customer.Customer],
):
    def _build(order: dict) -> ResultE[sales_order.Order]:
        with restlet_repo.netsuite_session() as session:
            return Fold.collect_all(
                [
                    item_repo.build(
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
                    **ecom,  # type: ignore
                    **sales_order_repo.build_detail(memo_builder(order)),
                }
            )

    return _build


def create(order: sales_order.Order) -> ResultE[int]:
    with restlet_repo.netsuite_session() as session:
        return flow(  # type: ignore
            order,
            bind(sales_order_repo.build(session)),
            bind(sales_order_repo.create(session)),
            map_(lambda x: x["id"]),  # type: ignore
        )


def close(order: sales_order.Order) -> ResultE[int]:
    with restlet_repo.netsuite_session() as session:
        return flow(  # type: ignore
            order,
            lambda x: x["order"]["id"],
            bind(sales_order_repo.close(session)),
            map_(lambda x: int(x["id"])),  # type: ignore
        )
