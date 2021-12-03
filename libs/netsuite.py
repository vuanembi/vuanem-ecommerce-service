from typing import Optional

from requests_oauthlib import OAuth1Session


from libs import restlet
from models.order import Order
from models.customer import CustomerRequest
from models.ecommerce import LEAD_SOURCE


def get_customer_if_not_exist(session: OAuth1Session, customer: CustomerRequest) -> str:
    _customer = restlet.customer("GET")(session, params={"phone": customer["phone"]})
    return (
        _customer["id"]
        if _customer
        else restlet.customer("POST")(
            session,
            body={
                "leadsource": LEAD_SOURCE,
                "firstname": customer["firstname"],
                "lastname": customer["lastname"],
                "phone": customer["phone"],
            },
        )["id"]
    )


def map_sku_to_item_id(session: OAuth1Session, sku: str) -> Optional[str]:
    try:
        return restlet.inventory_item("GET")(session, params={"itemid": sku})["id"]
    except:
        return None


def create_sales_order(session: OAuth1Session, order: Order) -> str:
    return restlet.sales_order("POST")(session, body=order)["id"]
