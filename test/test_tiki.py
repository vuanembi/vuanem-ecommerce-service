import pytest
from returns.result import Success
from returns.pipeline import is_successful

from tiki import tiki_service, tiki_repo, auth_repo, event_repo, seller

from test.conftest import run


@pytest.fixture()
def state():
    return tiki_repo.TIKI


@pytest.fixture()
def auth_session():
    return tiki_service.auth_service()


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


class TestEvent:
    def test_get_ack_id(self):
        res = event_repo.get_ack_id()
        assert is_successful(res)

    def test_update_ack_id(self):
        res = event_repo.update_ack_id("6b405afc-25d6-4634-a2f1-a20e80bcf5bf")
        assert is_successful(res)

    def test_pull_service(self, auth_session):
        ack_id, events = tiki_service._pull_service(auth_session).unwrap()
        assert ack_id
        assert events


class TestTikiOrder:
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
        return Success(order_id).bind(tiki_repo.get_order(auth_session))

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
                        # "phone": "0938169869",
                        "phone": "",
                    }
                },
            }
        )

    def test_get_order(self, order):
        res = order
        assert is_successful(res)

    def test_build_order(self, order, static_order):
        res1 = order.bind(seller.TIKI.order_builder)
        res2 = static_order.bind(tiki_service.builder)
        assert res1, res2

    def test_get_orders_service(self, auth_session, events):
        res = tiki_service._get_orders_service(auth_session, events)
        res

    def test_service(self):
        res = tiki_service.ingest_orders_service()
        res

    def test_controller(self):
        res = run("/tiki/orders/ingest")
        res


class TestProducts:
    def test_get_products_service(self):
        res = tiki_service.get_products_service()
        res

    def test_alert_products_service(self):
        res = tiki_service.alert_products_service()
        res

    def test_controller(self):
        res = run("/tiki/products")
        res
