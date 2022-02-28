from returns.pipeline import is_successful

from netsuite.query.analytics import analytics_service
from netsuite.sales_order import sales_order_repo, sales_order_service
from netsuite.customer import customer_repo
from netsuite.item import item_repo
from netsuite.order import order_service
from netsuite.journal_entry import journal_entry_controller

import pytest

from test.conftest import run


class TestItem:
    @pytest.mark.parametrize(
        ("sku", "test_fn"),
        [
            ("1206001016001", lambda x: x.unwrap() == "283790"),
            ("11111", lambda x: x),
        ],
        ids=[
            "success",
            "fail",
        ],
    )
    def test_map_sku_to_item_id(self, netsuite_session, sku, test_fn):
        res = item_repo.map_sku_to_item_id(netsuite_session, sku)
        assert test_fn(res)


class TestCustomer:
    def test_build(self, netsuite_session):
        exists_res = customer_repo.build(netsuite_session)("HM", "0773314403")
        new_res = customer_repo.build(netsuite_session)("Test HM", "07733144031998")
        assert exists_res.unwrap() == 599656
        assert is_successful(new_res)


class TestSalesOrder:
    def test_build(
        self,
        netsuite_session,
        prepared_order,
        netsuite_order,
    ):
        res_prepared = sales_order_repo.build(netsuite_session)(prepared_order)
        res = sales_order_repo.build(netsuite_session)(netsuite_order)
        assert res_prepared.unwrap() == netsuite_order
        assert res.unwrap() == netsuite_order

    def test_create_service(self, prepared_order):
        res = sales_order_service.create(prepared_order)
        assert res

    def test_close_service(self, prepared_order):
        res = sales_order_service.close(prepared_order)
        assert res


class TestOrder:
    @pytest.mark.parametrize(
        "id",
        [
            "03dbXLxJayed9gbWDvcN",
            "0CM8MOAl8H6VEINaYuIB",
        ],
        ids=[
            "success",
            "fail",
        ],
    )
    def test_create_service(self, id):
        res = order_service.create(id)
        assert res

    @pytest.mark.parametrize(
        "id",
        [
            "03dbXLxJayed9gbWDvcN",
            "0CM8MOAl8H6VEINaYuIB",
        ],
        ids=[
            "success",
            "fail",
        ],
    )
    def test_close_service(self, id):
        res = order_service.close(id)
        assert res


class TestAnalytics:
    @pytest.fixture()
    def coupon_codes(self):
        return [
            "0122-9KGOI-AGI02-0001",
            "0122-9KGOI-AGI02-0011",
        ]

    def test_coupon_code_analytics_service(self, coupon_codes):
        res = analytics_service.coupon_code_service({"data": coupon_codes})
        assert is_successful(res)

    def test_coupon_code_analytics_controller(self, coupon_codes):
        res = run("/netsuite/analytics/coupon_code", {"data": coupon_codes})
        assert res


class TestBankInTransit:
    @pytest.fixture(
        params=journal_entry_controller.services.items(),
        ids=[i.split("/")[-1] for i in journal_entry_controller.services.keys()],
    )
    def service(self, request):
        return request.param

    @pytest.fixture(
        params=[
            None,
            "2022-02-20",
        ],
    )
    def _date(self, request):
        return request.param

    def test_service(self, service, _date):
        res = service[1]({"date": _date})
        res

    def test_controller(self, service, _date):
        res = run(service[0], {"date": _date})
        res
