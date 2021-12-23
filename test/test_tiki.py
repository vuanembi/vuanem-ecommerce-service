import os
import uuid

import pytest
from returns.result import Success
from returns.pipeline import is_successful

from tiki import TikiController, TikiService, TikiAuthRepo, TikiDataRepo

from test.conftest import run


@pytest.fixture()
def fail_api_key():
    os.environ["TIKI_CLIENT_ID"] = uuid.uuid4()


class TestAuth:
    def test_get_new_access_token(self):
        res = TikiAuthRepo.get_new_access_token()
        assert is_successful(res)

    def test_persist_access_token(self):
        res = TikiAuthRepo.get_new_access_token().bind(
            TikiAuthRepo.persist_access_token
        )
        assert is_successful(res)

    def test_get_latest_access_token(self):
        res = TikiAuthRepo.get_latest_access_token()
        assert is_successful(res)

    def test_persist_new_access_token(self):
        res = TikiService._persist_new_access_token()
        assert is_successful(res)

    def test_auth_service(self, session):
        res = TikiService.auth_service(session)
        assert is_successful(res)


class TestData:
    @pytest.fixture()
    def headers(self, session):
        return TikiService.auth_service(session).unwrap()

    @pytest.fixture()
    def auth_session(self, session):
        TikiService.auth_service(session).bind(
            lambda x: Success(session.headers.update(x))
        )
        return session

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
        return Success(order_id).bind(TikiDataRepo.get_order(auth_session))

    def test_pull_service(self, auth_session):
        ack_id, events = TikiService.pull_service(auth_session)
        assert is_successful(ack_id)
        assert is_successful(events)

    def test_get_order(self, order):
        res = order
        assert is_successful(res)

    def test_get_orders(self, auth_session):
        _, events = TikiService.pull_service(auth_session)
        res = events.bind(
            lambda events: [
                TikiDataRepo.get_order(auth_session)(TikiDataRepo.extract_order(e))
                for e in events
            ]
        )
        assert res

    def test_add_item(self, order):
        res = order.bind(TikiService._add_items)
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
        res = order.bind(TikiService._add_customer)
        assert res == {
            "custbody_customer_phone": "0938169869",
            "custbody_recipient_phone": "0938169869",
            "custbody_recipient": "Nguyễn Vũ Ngọc Giang",
            "shippingaddress": {"addressee": "Nguyễn Vũ Ngọc Giang"},
        }

    def test_build_order(self, order):
        res = order.bind(TikiService._build_order)
        assert res

    def test_handle_order(self, order):
        res = order.bind(TikiService._handle_order)
        assert res

    def test_events_service(self, auth_session, events):
        res = TikiService.events_service(auth_session)(events)
        res


class TestIntegration:
    def test_controller_success(self):
        res = TikiController.tiki_controller({})
        assert res

    def test_controller_fail(self):
        with pytest.raises(Exception) as e:
            res = TikiController.tiki_controller({})
            assert res

    def test_tiki(self):
        res = run("/tiki")
        res
