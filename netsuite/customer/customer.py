from typing import TypedDict, Optional


LEAD_SOURCE = 144506

ADDRESS__CITYPROVINCE = 66
ADDRESS__DISTRICT = 1

SHIPPING_ADDRESS_SEPARATOR = ";"

ROOT_ADDRESS = f"{SHIPPING_ADDRESS_SEPARATOR} ".join(
    [
        "Số 1 Đào Duy Anh",
        "Phương Mai",
        "Đống Đa",
        "Hà Nội",
        "Việt Nam",
    ]
)


class ShippingAddress(TypedDict):
    addressee: str
    custrecord_cityprovince: int
    custrecord_districts: int


class Customer(TypedDict):
    entity: Optional[int]
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress
    shipaddress: str


class CustomerReq(TypedDict):
    subsidiary: int
    leadsource: int
    phone: str
    firstname: str
    lastname: str
