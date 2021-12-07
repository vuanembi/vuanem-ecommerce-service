import requests
import pytest

from libs.restlet import netsuite_session
from models.netsuite import order


@pytest.fixture()
def session():
    return requests.Session()


@pytest.fixture()
def oauth_session():
    return netsuite_session()


@pytest.fixture()
def prepared_order() -> order.PreparedOrder:
    return {
        "custbody_customer_phone": "0773314403",
        "custbody_expecteddeliverytime": 4,
        "custbody_recipient": "Hieu",
        "custbody_recipient_phone": "0773314403",
        "shippingaddress": {"addressee": "anh Hiếu", "country": "VN"},
        "custbody_order_payment_method": 22,
        "salesrep": 1666,
        "trandate": "2021-10-26",
        "leadsource": 144506,
        "partner": 916906,
        "custbody_onl_rep": 942960,
        "location": 788,
        "item": [{"item": 5057, "quantity": 2, "price": -1, "amount": 100000}],
    }
