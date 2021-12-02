from typing import TypedDict, Optional

import requests

import restlet

LEAD_SOURCE = 144506


class Customer(TypedDict):
    phone: str
    firstname: str
    lastname: str


def get_customer_if_not_exist(session: requests.Session, customer: Customer) -> str:
    try:
        return restlet.customer("GET")(session, params={"phone": customer["phone"]})[
            "id"
        ]
    except:
        return restlet.customer("POST")(
            session,
            body={
                "leadsource": LEAD_SOURCE,
                "firstname": customer["firstname"],
                "lastname": customer["lastname"],
                "phone": customer["phone"],
            },
        )["id"]


def map_sku_to_item_id(session: requests.Session, sku: str) -> Optional[str]:
    try:
        return restlet.inventory_item("GET")(session, params={"itemid": sku})["id"]
    except:
        return None


def create_ecommerce_sales_order(session: requests.Session, order, customer, ecommerce):
    pass
