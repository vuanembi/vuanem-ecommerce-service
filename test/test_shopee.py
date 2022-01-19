from datetime import datetime

from returns.pipeline import is_successful

import pytest

from shopee import shopee_service, auth_repo, data_repo

from test.conftest import run


class TestAuth:
    def test_get_token(self, session):
        res = auth_repo.get_token(session, "4d415a73444447417278654f704b575a")
        res

    def test_refresh_token(self, session):
        res = auth_repo.refresh_token(
            session,
            {
                "refresh_token": "5748426a7877766343674f51594b786b",
            },
        )
        res

    def test_auth_service(self):
        res = shopee_service.auth_service()
        res


class TestData:
    @pytest.fixture()
    def auth_builder(self):
        return shopee_service.auth_service().unwrap()

    def test_get_orders(self, session, auth_builder):
        res = data_repo.get_orders(session, auth_builder)(
            int(datetime(2022, 1, 10).timestamp())
        )
        assert is_successful(res)

    def test_get_orders_items(self, auth_builder):
        res = shopee_service._get_orders_items(
            auth_builder,
            int(datetime(2022, 1, 10).timestamp()),
        )
        res

    def test_get_orders_service(self):
        res = shopee_service.get_orders_service()
        res


class TestIntegration:
    def test_controller(self):
        res = run("/shopee")
        res

