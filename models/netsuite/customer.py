from typing import TypedDict


class ShippingAddress(TypedDict):
    addressee: str


class PreparedCustomer(TypedDict):
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress


class Customer(PreparedCustomer):
    entity: int


class CustomerRequest(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str
