from typing import TypedDict

from models.netsuite.ecommerce import LEAD_SOURCE


class ShippingAddress(TypedDict):
    addressee: str


class CustomerBase(TypedDict):
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress


class Customer(CustomerBase):
    entity: int


class PreparedCustomer(CustomerBase):
    entity: None


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


def build_prepared_customer(phone: str, name: str) -> PreparedCustomer:
    return {
        "entity": None,
        "custbody_customer_phone": phone,
        "custbody_recipient_phone": phone,
        "custbody_recipient": name,
        "shippingaddress": {
            "addressee": name,
        },
    }
