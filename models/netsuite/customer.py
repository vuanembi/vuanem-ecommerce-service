from typing import TypedDict

from models.netsuite import ecommerce


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
    leadsource: ecommerce.LEAD_SOURCE
    phone: str
    firstname: str
    lastname: str
