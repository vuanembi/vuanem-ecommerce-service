from collections import OrderedDict
import requests
import pytest
import random

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
    return OrderedDict(
        {
            "trandate": "2021-10-26",
            "subsidiary": 1,
            "location": 788,
            "department": 1044,
            "custbody_customer_phone": "0773314403",
            "custbody_expecteddeliverytime": 4,
            "custbody_recipient": "Hieu",
            "custbody_recipient_phone": "0773314403",
            "shippingaddress": {"addressee": "anh Hiếu", "country": "VN"},
            "custbody_order_payment_method": 22,
            "salesrep": 1666,
            "leadsource": 144506,
            "partner": 916906,
            "custbody_onl_rep": 942960,
            "item": [{"item": 5057, "quantity": 2, "price": -1, "amount": 100000}],
        }
    )


@pytest.fixture()
def netsuite_order(prepared_order):
    return OrderedDict(
        {
            "entity": 599656,
            **prepared_order,
        }
    )


@pytest.fixture()
def update():
    return {
        "update_id": random.randint(100000, 900000),
        "callback_query": {
            "id": "3662730095478523210",
            "from": {
                "id": 852795805,
                "is_bot": False,
                "first_name": "HM",
                "username": "hieumdd",
                "language_code": "en",
            },
            "message": {
                "message_id": 25,
                "from": {
                    "id": 2011095877,
                    "is_bot": True,
                    "first_name": "Bot Bắn Đơn",
                    "username": "vuanembi_ecommercebot",
                },
                "chat": {
                    "id": -645664226,
                    "title": "HM & Bot Bắn Đơn",
                    "type": "group",
                    "all_members_are_administrators": True,
                },
                "date": 1638870628,
                "text": "Đơn hàng Tiki mới\n===========\ncode: '678789503'\nid: 131999047\nitems:\n- invoice:\n    row_total: 6299000\n  product:\n    name: Giường ngủ gỗ cao su Amando Cherry vững chắc, phong cách hiện đại, nâng\n      đỡ tốt - 160x200\n    seller_product_code: '1404003002002'\n  qty: 1\nshipping:\n  address:\n    district: Thành phố Nha Trang\n    full_name: Nguyễn Vũ Ngọc Giang\n    phone: 0938169869\n    street: 36A Cù Lao Trung\n    ward: Phường Vĩnh Thọ",
                "entities": [
                    {"offset": 9, "length": 4, "type": "bold"},
                    {"offset": 30, "length": 406, "type": "pre"},
                ],
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Tạo đơn (+)",
                                "callback_data": '{"t": "O", "a": 1, "v": "pI9Jog6n1fFkNsVk4x7Y"}',
                            },
                            {
                                "text": "Huỷ đơn (-)",
                                "callback_data": '{"t": "O", "a": -1, "v": "pI9Jog6n1fFkNsVk4x7Y"}',
                            },
                        ]
                    ]
                },
            },
            "chat_instance": "8890303927539922236",
            "data": '{"t": "O", "a": 1, "v": "dcKwUknGf8eY2vePOJVA"}',
        },
    }


@pytest.fixture()
def prepared_order_id():
    return "dcKwUknGf8eY2vePOJVA"


@pytest.fixture()
def callback_data():
    return {"t": "O", "a": 1, "v": "dcKwUknGf8eY2vePOJVA"}
