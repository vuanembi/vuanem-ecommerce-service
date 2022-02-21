from typing import TypedDict, Any

from netsuite.sales_order import sales_order


class Order(TypedDict):
    source: Any
    order: sales_order.Order
    status: str
    created_at: str
    updated_at: str
    is_deleted: bool


class OrderRequest(TypedDict):
    id: str
