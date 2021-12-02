from typing import TypedDict

from restlet import (
    create_sales_order,
    get_customer,
    create_customer,
    get_inventory_item,
)


class Customer(TypedDict):
    phone: str
    firstname: str
    lastname: str


def get_customer_if_not_exist(session, customer: Customer):
    try:
        return get_customer(session, params={"phone": customer["phone"]})["id"]
    except:
        return create_customer(
            session,
            body={
                "leadsource": 144506,
                "firstname": customer["firstname"],
                "lastname": customer["lastname"],
                "phone": customer["phone"],
            },
        )["id"]

def map_sku_to_item_id(session, sku):
    try:
        return get_inventory_item(session, params={"itemid": sku})
    except:
        return None


