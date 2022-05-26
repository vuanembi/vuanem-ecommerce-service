from datetime import datetime

from returns.pipeline import is_successful

import pytest

from shopee import shopee_service, shopee_repo, auth_repo, shopee_controller

from test.conftest import run


@pytest.fixture(
    params=shopee_controller.sellers.values(),
    ids=shopee_controller.sellers.keys(),
)
def seller(request):
    return request.param


class TestAuth:
    def test_get_token(self, seller, session):
        res = auth_repo.get_token(seller, session, "5555555243484b634e64736369514354")
        res

    def test_refresh_token(self, seller, session):
        res = auth_repo.refresh_token(
            seller,
            session,
            {
                "refresh_token": "5748426a7877766343674f51594b786b",
            },
        )
        res

    def test_auth_service(self, seller):
        res = shopee_service._auth_service(seller)
        res


class TestOrder:
    @pytest.fixture()
    def auth_builder(self):
        return shopee_service._auth_service().unwrap()

    def test_get_orders(self, session, auth_builder):
        res = shopee_repo.get_orders(session, auth_builder)(
            int(datetime(2022, 1, 10).timestamp())
        )
        assert is_successful(res)

    def test_get_orders_items(self, auth_builder):
        res = shopee_service._get_orders_items(
            auth_builder,
            int(datetime(2022, 1, 10).timestamp()),
        )
        res

    def test_service(self, seller):
        res = shopee_service.ingest_orders_service(seller)
        res

    def test_controller(self, seller):
        res = run("/shopee/orders/ingest", {"seller": seller.name})
        res


class TestItems:
    def test_get_items_service(self):
        res = shopee_service.get_items_service()
        res

    def test_controller(self):
        res = run("/shopee/items")
        res
