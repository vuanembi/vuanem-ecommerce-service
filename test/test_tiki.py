import os
import uuid

import pytest
from returns.result import Success
from returns.pipeline import is_successful

from tiki import tiki_controller, tiki_service, auth_repo, data_repo

from test.conftest import run


@pytest.fixture()
def fail_api_key():
    os.environ["TIKI_CLIENT_ID"] = uuid.uuid4()


class TestAuth:
    @pytest.mark.parametrize(
        "token",
        [
            auth_repo._access_token.document("access_token").get().to_dict(),
            auth_repo._access_token.document("access_token_expired").get().to_dict(),
        ],
        ids=[
            "live",
            "expired",
        ],
    )
    def test_get_auth_session(self, token):
        res = auth_repo.get_auth_session(token)
        assert res.token.is_expired() == False

    def test_auth_service(self):
        res = tiki_service.auth_service()
        assert res.token.is_expired() == False


class TestData:
    @pytest.fixture()
    def auth_session(self):
        return tiki_service.auth_service()

    @pytest.fixture()
    def events(self):
        return [
            {
                "id": "355a53df-e14b-48d5-83f0-0c3ae55e4b20",
                "sid": "0E2CF3DF79B8CCEB098E86174C79D89F6BDDBF2D",
                "created_at": 1639123927592,
                "payload": {"order_code": "751449845"},
                "type": "ORDER_CREATED_SUCCESSFULLY",
                "version": "v1",
            }
        ]

    @pytest.fixture()
    def order_id(self):
        return "678789503"

    @pytest.fixture()
    def order(self, auth_session, order_id):
        return Success(order_id).bind(data_repo.get_order(auth_session))

    def test_get_ack_id(self):
        res = data_repo.get_ack_id()
        assert is_successful(res)

    def test_update_ack_id(self):
        res = data_repo.update_ack_id("6b405afc-25d6-4634-a2f1-a20e80bcf5bf")
        assert is_successful(res)

    def test_pull_service(self, auth_session):
        ack_id, events = tiki_service.pull_service(auth_session)
        assert is_successful(ack_id)
        assert is_successful(events)

    def test_get_order(self, order):
        res = order
        assert is_successful(res)

    def test_get_orders(self, auth_session):
        _, events = tiki_service.pull_service(auth_session)
        res = events.bind(
            lambda events: [
                data_repo.get_order(auth_session)(data_repo.extract_order(e))
                for e in events
            ]
        )
        assert res

    def test_add_item(self, order):
        res = order.bind(tiki_service._add_items)
        assert res == {
            "item": [
                {
                    "item": 196870,
                    "quantity": 1,
                    "price": -1,
                    "amount": 5726363,
                },
            ],
        }

    def test_add_customer(self, order):
        res = order.bind(tiki_service._add_customer)
        assert res == {
            "custbody_customer_phone": "0938169869",
            "custbody_recipient_phone": "0938169869",
            "custbody_recipient": "Nguyễn Vũ Ngọc Giang",
            "shippingaddress": {"addressee": "Nguyễn Vũ Ngọc Giang"},
        }

    def test_build_order(self, order):
        res = order.bind(tiki_service._build_order)
        assert res

    def test_handle_order(self, order):
        res = order.bind(tiki_service._handle_order)
        assert res

    def test_events_service(self, auth_session, events):
        res = tiki_service.events_service(auth_session)(events)
        res


class TestIntegration:
    def test_controller_success(self):
        res = tiki_controller.tiki_controller({})
        assert res

    def test_controller_fail(self):
        with pytest.raises(Exception) as e:
            res = tiki_controller.tiki_controller({})
            assert res

    def test_tiki(self):
        res = run("/tiki")
        res
