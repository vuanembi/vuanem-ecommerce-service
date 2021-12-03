from typing import TypedDict

from models.ecommerce import LEAD_SOURCE


class ShippingAddress(TypedDict):
    addressee: str


class Customer(TypedDict):
    entity: int
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress


class CustomerRequest(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str


def build_customer_request(name, phone) -> CustomerRequest:
    return {
        "leadsource": LEAD_SOURCE,
        "firstname": "Anh Chị",
        "lastname": name,
        "phone": phone,
    }


def build(id: str, phone: str, name: str) -> Customer:
    return {
        "entity": int(id),
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }
