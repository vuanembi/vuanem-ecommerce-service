from typing import Optional

from requests_oauthlib import OAuth1Session
from returns.result import ResultE, Failure, safe
from returns.pipeline import flow
from returns.pointfree import map_, lash, bind

from netsuite.customer import customer
from netsuite.restlet import restlet, restlet_repo
from netsuite.query import query_service
from netsuite.query.saved_search import saved_search


def add_shipping_address(components: list[str]) -> str:
    return f"{customer.SHIPPING_ADDRESS_SEPARATOR} ".join(components)


def add(
    default: customer.Customer,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    address: Optional[str] = None,
) -> customer.Customer:
    return (
        {
            "entity": None,
            "custbody_customer_phone": phone,
            "custbody_recipient_phone": phone,
            "custbody_recipient": name,
            "shippingaddress": {
                "addressee": name,
            },
            "shipaddress": address,
        }
        if phone and name and address
        else default
    )


def serialize_shipping_address(address: str) -> str:
    return "\n".join(
        [i.strip() for i in address.split(customer.SHIPPING_ADDRESS_SEPARATOR)]
    )


def _build_request(name: str, phone: str) -> customer.CustomerReq:
    return {
        "leadsource": customer.LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def _get(session: OAuth1Session):
    def _req(customer_req: customer.CustomerReq) -> ResultE[str]:
        return flow(
            {
                "id": saved_search.SavedSearch.Customer.value,
                "filterExp": [["phone", "contains", customer_req["phone"]]],
            },
            query_service.saved_search_service(session),
            bind(safe(lambda x: x[0]["internalid"])),
        )

    return _req


def _create(session: OAuth1Session):
    def _req(customer_req: customer.CustomerReq) -> ResultE[str]:
        return restlet_repo.request(
            session,
            restlet.Record,
            "POST",
            body={
                "type": "customer",
                "data": {
                    "leadsource": customer.LEAD_SOURCE,
                    "firstname": customer_req["firstname"],
                    "lastname": customer_req["lastname"],
                    "phone": customer_req["phone"],
                },
            },
        ).map(lambda x: x["id"])

    return _req


def build(session: OAuth1Session):
    def _build(name_phone: tuple[str, str]) -> ResultE[int]:
        name, phone = name_phone
        customer_req = _build_request(name, phone)
        return flow(
            customer_req,
            _get(session),
            lash(lambda _: Failure(customer_req)),  # type: ignore
            lash(_create(session)),
            map_(int),
        )

    return _build
