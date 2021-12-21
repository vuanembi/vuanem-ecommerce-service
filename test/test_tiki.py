import pytest
from returns.pipeline import is_successful

from tiki import TikiService, TikiAuthRepo, TikiDataRepo

# from libs.firestore import get_latest_tiki_ack_id
# from libs.telegram import send_new_order

class TestAuth:
    def test_get_new_access_token(self):
        res = TikiAuthRepo.get_new_access_token()
        assert is_successful(res) is True

    def test_persist_access_token(self):
        res = TikiAuthRepo.get_new_access_token().bind(
            TikiAuthRepo.persist_access_token
        )
        res

    def test_get_latest_access_token(self):
        res = TikiAuthRepo.get_latest_access_token()
        res

    def test_access_token_service(self):
        res = TikiService.persist_new_access_token()
        res

    def test_authenticate(self, session):
        res = TikiService.authenticate(session)
        res


class TestData:
    @pytest.fixture()
    def headers(self, session):
        return TikiService.authenticate(session)

    @pytest.fixture()
    def order_id(self):
        return "678789503"

    @pytest.fixture()
    def order(self, session, headers, order_id):
        return TikiDataRepo.get_order(session, headers)(order_id)

    def test_get_order(self, order):
        res = order
        assert res

    def test_add_item(self, order):
        res = order.bind(TikiService.add_items)
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
        res = order.bind(TikiService.add_customer)
        assert res == {
            "custbody_customer_phone": "0938169869",
            "custbody_recipient_phone": "0938169869",
            "custbody_recipient": "Nguyễn Vũ Ngọc Giang",
            "shippingaddress": {"addressee": "Nguyễn Vũ Ngọc Giang"},
        }

    def test_build_prepared_order(self, order):
        res = order.bind(TikiService.build_prepared_order)
        assert res

    def test_persist_prepared_order(self, session, headers, order_id):
        res = TikiService.persist_prepared_order(session, headers, order_id)
        res


# def test_pull_event(session):
#     ack_id, events = pull_events(session, get_latest_tiki_ack_id())
#     assert ack_id


# def test_alert_on_order(order):
#     res = send_new_order("TIKI", order)
#     assert res

# def test_send_new_order(order):
#     assert send_new_order("Tiki", order, "111")["ok"]


# def test_handle_orders(order):
#     assert handle_orders({"orders": [order]})["orders"]


# def test_tiki():
#     res = run("/tiki")
#     assert res["ack_id"]
