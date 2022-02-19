from typing import Optional

from requests_oauthlib import OAuth1Session
from returns.result import ResultE
from returns.pipeline import flow
from returns.pointfree import map_, lash

from netsuite.customer import customer
from netsuite.restlet import restlet, restlet_repo


def add(
    default: customer.Customer,
    phone: Optional[str] = None,
    name: Optional[str] = None,
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
        }
        if phone and name
        else default
    )


def _build_request(name: str, phone: str) -> customer.CustomerReq:
    return {
        "leadsource": customer.LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def _get(session: OAuth1Session):
    def _req(customer_req: customer.CustomerReq) -> ResultE[dict[str, str]]:
        return restlet_repo.request(
            session,
            restlet.Customer,
            "GET",
            params={
                "phone": customer_req["phone"],
            },
        )

    return _req


def _create(session: OAuth1Session):
    def _req(customer_req: customer.CustomerReq) -> ResultE[dict[str, str]]:
        return restlet_repo.request(
            session,
            restlet.Customer,
            "POST",
            body={
                "leadsource": customer.LEAD_SOURCE,
                "firstname": customer_req["firstname"],
                "lastname": customer_req["lastname"],
                "phone": customer_req["phone"],
            },
        )

    return _req


def build(session: OAuth1Session):
    def _build(name: str, phone: str) -> ResultE[int]:
        customer_req = _build_request(name, phone)
        return flow(
            customer_req,
            _get(session),
            lash(lambda _: Failure(customer_req)),  # type: ignore
            lash(_create(session)),
            map_(lambda x: x["id"]),  # type: ignore
            map_(int),
        )

    return _build
