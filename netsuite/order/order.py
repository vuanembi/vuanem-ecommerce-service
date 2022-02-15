from typing import TypedDict

from netsuite.sales_order import sales_order

class Order(TypedDict):
    # ! TODO
    source: dict
    order: sales_order.Order
    status: str
    transaction_id: int
    created_at: str
    updated_at: str
    is_deleted: bool
