from typing import TypedDict


class ShippingAddress(TypedDict):
    addressee: str

class Customer(TypedDict):
    entity: int
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress

