import os
import uuid

import pytest
from returns.result import Success
from returns.pipeline import is_successful

from tiki import tiki_controller, tiki_service, auth_repo, data_repo, tiki_repo

from test.conftest import run


@pytest.fixture()
def fail_api_key():
    os.environ["TIKI_CLIENT_ID"] = uuid.uuid4()


@pytest.fixture()
def state():
    return tiki_repo.TIKI


class TestAuth:
    @pytest.mark.parametrize(
        "token",
        [
            "access_token",
            "access_token_expired",
        ],
    )
    def test_get_auth_session(self, state, token):
        res = auth_repo.get_auth_session(state.get().to_dict()["state"][token])
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

    @pytest.fixture()
    def static_order(self):
        return Success(
            {
                "id": 131999047,
                "code": "678789503",
                "items": [
                    {
                        "product": {
                            "name": "Giường ngủ gỗ cao su Amando Cherry vững chắc, phong cách hiện đại, nâng đỡ tốt - 160x200",
                            "seller_product_code": "",
                        },
                        "seller_income_detail": {"item_qty": 1, "sub_total": 6334000},
                    },
                    {
                        "product": {
                            "name": "Giường ngủ gỗ cao su Amando Cherry vững chắc, phong cách hiện đại, nâng đỡ tốt - 160x200",
                            "seller_product_code": "",
                        },
                        "seller_income_detail": {"item_qty": 1, "sub_total": 6334000},
                    },
                ],
                "shipping": {
                    "address": {
                        "full_name": "Nguyễn Vũ Ngọc Giang",
                        "street": "36A Cù Lao Trung",
                        "ward": "Phường Vĩnh Thọ",
                        "district": "Thành phố Nha Trang",
                        "phone": "0938169869",
                    }
                },
            }
        )

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

    def test_build_order(self, order, static_order):
        res1 = order.bind(tiki_service._build_prepared_order)
        res2 = static_order.bind(tiki_service._build_prepared_order)
        assert res1, res2

    def test_handle_order(self, order):
        res = order.bind(tiki_service._handle_order)
        assert res

    def test_order_service(self, auth_session, events):
        res = tiki_service.order_service(auth_session)(events)
        res

    def test_events_service(self, auth_session, events):
        res = tiki_service.events_service(auth_session)(("1111", events))
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
