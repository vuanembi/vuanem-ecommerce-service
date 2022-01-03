from returns.result import Failure
from returns.pipeline import is_successful

import pytest

from lazada import lazada_controller, lazada_service, auth_repo, data_repo


class TestAuth:
    @pytest.fixture()
    def access_token(self):
        return {
            "access_token": "",
            "country": "vn",
            "refresh_token": "",
            "account_platform": "seller_center",
            "refresh_expires_in": 15552000,
            "country_user_info": [
                {
                    "country": "vn",
                    "user_id": "100553588",
                    "seller_id": "1000277583",
                    "short_code": "VNJ2K34I",
                }
            ],
            "expires_in": 2592000,
            "account": "duong.nguyen3@vuanem.com.vn",
            "code": "0",
            "request_id": "214100f016411257621594163",
            # "expires_at": 1640970000 + 2592000,
            "expires_at": 1640970000 - 2592000,
        }

    def test_get_access_token(self, access_token):
        res = auth_repo.get_access_token().unwrap()
        res

    def test_update_access_token(self, access_token):
        res = auth_repo.update_access_token(access_token)
        res

    def test_refresh_token(self, access_token, session):
        res = auth_repo.refresh_token(session, access_token)
        res

    def test_expired_token(self, access_token, session):
        res = Failure(access_token).lash(lazada_service._update_new_token(session))
        res

    def test_auth_service(self, session):
        res = lazada_service.auth_service(session)
        assert is_successful(res)


class TestData:
    @pytest.fixture()
    def auth_builder(self, session):
        return lazada_service.auth_service(session).unwrap()

    def test_get_orders(self, session, auth_builder):
        res = data_repo.get_orders(session, auth_builder, "2022-01-01T00:00:00")
        assert is_successful(res)

    def test_get_order_item(self, session, auth_builder):
        res = data_repo.get_order_item(session, auth_builder, "330337506104790")
        assert is_successful(res)

    def test_items(self, session, auth_builder):
        res = lazada_service.get_items(
            session,
            auth_builder,
            [
                {"order_id": 329803872615793, "created_at": "2021-12-31T16:12:03"},
                {"order_id": 331225193824299, "created_at": "2021-12-31T16:37:22"},
            ],
        )
        res

    def test_get_order_details(self, session, auth_builder):
        res = lazada_service.get_order_details(session, auth_builder)
        res

    def test_get_max_created_at(self):
        res = data_repo.get_max_created_at()
        res

class TestIntegration:
    def test_controller(self):
        res = lazada_controller.lazada_controller({})
        res
