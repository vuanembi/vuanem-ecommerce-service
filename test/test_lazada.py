from datetime import datetime

from returns.result import Failure
from returns.pipeline import is_successful

import pytest

from lazada import lazada_controller, lazada_service, auth_repo, lazada_repo, order_repo

from test.conftest import run


@pytest.fixture(
    params=lazada_controller.sellers.values(),
    ids=lazada_controller.sellers.keys(),
)
def seller(request):
    return request.param


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

    def test_get_access_token(self, seller):
        res = auth_repo.get_access_token(seller).unwrap()
        res

    def test_update_access_token(self, seller, access_token):
        res = auth_repo.update_access_token(seller)(access_token)
        res

    def test_refresh_token(self, access_token, session):
        res = auth_repo.refresh_token(session, access_token)
        res

    def test_auth_service(self, seller):
        res = lazada_service._auth_service(seller)
        assert is_successful(res)


class TestOrders:
    @pytest.fixture()
    def auth_builder(self, seller):
        return lazada_service._auth_service(seller).unwrap()

    def test_get_orders(self, session, auth_builder):
        res = lazada_repo.get_orders(session, auth_builder)(datetime(2022, 2, 15))
        assert is_successful(res)

    def test_items(self, session, auth_builder):
        res = lazada_service._get_items(
            session,
            auth_builder,
            [
                {"order_id": 329803872615793, "created_at": "2021-12-31T16:12:03"},
                {"order_id": 331225193824299, "created_at": "2021-12-31T16:37:22"},
            ],
        )
        res

    def test_get_orders_items(self, seller, session, auth_builder):
        created_after = order_repo.get_max_created_at(seller)
        res = created_after.bind(lazada_repo.get_orders(session, auth_builder))
        res

    def test_get_max_created_at(self, seller):
        res = order_repo.get_max_created_at(seller)
        res

    def test_service(self, seller):
        res = lazada_service.ingest_orders_service(seller)
        res

    def test_controller(self, seller):
        res = run("/lazada/orders/ingest", {"seller": seller.name})
        res


class TestProducts:
    def test_service(self):
        res = lazada_service.get_products_service()
        res

    def test_controller(self):
        res = run("/lazada/products")
        res
