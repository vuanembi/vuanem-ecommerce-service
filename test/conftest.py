from typing import Optional
from unittest.mock import Mock
import json

import requests
import pytest

from netsuite.sales_order import sales_order
from netsuite.restlet import restlet_repo
from main import main


@pytest.fixture()
def session():
    return requests.Session()


@pytest.fixture()
def netsuite_session():
    return restlet_repo.netsuite_session()


def run(path: str, data: Optional[dict] = None, method: str = "POST") -> dict:
    return main(
        Mock(
            get_json=Mock(return_value=data),
            path=path,
            args=data,
            method=method,
        )
    )


@pytest.fixture()
def prepared_order() -> sales_order.Order:
    return {
        "entity": None,
        "trandate": "2021-10-26",
        "shipdate": "2021-10-29",
        "subsidiary": 1,
        "location": 788,
        "department": 1044,
        "custbody_customer_phone": "0773314403",
        "custbody_expecteddeliverytime": 4,
        "custbody_recipient": "Hieu",
        "custbody_recipient_phone": "0773314403",
        "shippingaddress": {"addressee": "anh Hiếu"},
        "shipaddress": "\n".join(["Test", "test", "test"]),
        "custbody_order_payment_method": 23,
        "custbody_expected_shipping_method": 4,
        "custbody_print_form": True,
        "memo": "Đơn test",
        "salesrep": 1666,
        "leadsource": 144506,
        "partner": 916906,
        "custbody_onl_rep": 942960,
        "item": [
            {
                "item": 5057,
                "quantity": 2,
                "price": -1,
                "amount": 100000,
                "commitinventory": 3,
                "location": 788,
                "custcol_deliver_location": 50,
            }
        ],
    }


@pytest.fixture()
def netsuite_order(prepared_order):
    return {
        "entity": 599656,
        **prepared_order,
    }


@pytest.fixture()
def prepared_order_id():
    return "KI0mh4zAaCu02w1fniGL"


@pytest.fixture()
def message_id():
    return 643


@pytest.fixture()
def callback_data(prepared_order_id):
    return json.dumps({"t": "O", "a": -1, "v": prepared_order_id})


@pytest.fixture()
def chat_id():
    return -645664226


@pytest.fixture()
def telegram_update(callback_data, chat_id, message_id):
    return {
        "update_id": 724516415,
        "callback_query": {
            "id": "3662730096086300294",
            "from": {
                "id": 852795805,
                "is_bot": True,
                "first_name": "HM",
                "username": "hieumdd",
                "language_code": "en",
            },
            "message": {
                "message_id": message_id,
                "from": {
                    "id": 5028559722,
                    "is_bot": True,
                    "first_name": "vuanembi_ecommercebot_dev",
                    "username": "vuanembi_ecommerce_dev_bot",
                },
                "chat": {
                    "id": chat_id,
                    "title": "HM & Bot Bắn Đơn",
                    "type": "group",
                    "all_members_are_administrators": True,
                },
                "date": 1641388011,
                "text": "Đơn hàng Tiki mới\n===========\ncode: '929540084'\nid: 136344254\nitems:\n- product:\n    name: 'Gối Memory Foam Aeroflow iCool 45x65 giúp ngủ sâu, giảm đau cổ vai gáy,\n      phù hợp với mọi tư thế nằm '\n    seller_product_code: '1301009003001'\n  seller_income_detail:\n    item_qty: 1\n    sub_total: 765000\nshipping:\n  address:\n    district: Quận Hà Đông\n    full_name: nguyễn thành trung\n    phone: ''\n    street: lk2a26 nguyễn văn trỗi (đối diện số 74 nguyễn văn trỗi)\n    ward: Phường Mộ Lao",
                "entities": [
                    {"offset": 9, "length": 4, "type": "bold"},
                    {"offset": 30, "length": 458, "type": "pre"},
                ],
                "reply_markup": {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Tạo đơn",
                                "callback_data": callback_data,
                            }
                        ]
                    ]
                },
            },
            "chat_instance": "-1721483670851371259",
            "data": callback_data,
        },
    }
