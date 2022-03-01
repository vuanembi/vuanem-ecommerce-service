from typing import TypedDict, Optional


LEAD_SOURCE = 144506


class ShippingAddress(TypedDict):
    addressee: str


class Customer(TypedDict):
    entity: Optional[int]
    custbody_customer_phone: str
    custbody_recipient_phone: str
    custbody_recipient: str
    shippingaddress: ShippingAddress
    shipaddress: str


class CustomerReq(TypedDict):
    leadsource: int
    phone: str
    firstname: str
    lastname: str


TIKI_CUSTOMER: Customer = {
    "entity": None,
    "custbody_customer_phone": "1998103102",
    "custbody_recipient_phone": "1998103102",
    "custbody_recipient": "TEMP Tiki",
    "shippingaddress": {
        "addressee": "TEMP Tiki",
    },
    "shipaddress": "Số 1 Đào Duy Anh|Phương Mai|Đống Đa|Hà Nội|Việt Nam",
}

LAZADA_CUSTOMER: Customer = {
    "entity": None,
    "custbody_customer_phone": "1998103103",
    "custbody_recipient_phone": "1998103103",
    "custbody_recipient": "TEMP Lazada",
    "shippingaddress": {
        "addressee": "TEMP Lazada",
    },
    "shipaddress": "Số 1 Đào Duy Anh|Phương Mai|Đống Đa|Hà Nội|Việt Nam",
}

SHOPEE_CUSTOMER: Customer = {
    "entity": None,
    "custbody_customer_phone": "1998103101",
    "custbody_recipient_phone": "1998103101",
    "custbody_recipient": "TEMP Shopee",
    "shippingaddress": {
        "addressee": "TEMP Shopee",
    },
    "shipaddress": "Số 1 Đào Duy Anh|Phương Mai|Đống Đa|Hà Nội|Việt Nam",
}
