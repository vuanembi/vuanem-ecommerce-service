from returns.pipeline import is_successful

from netsuite.query.analytics import analytics_service
from netsuite.sales_order import sales_order_repo, sales_order_service
from netsuite.customer import customer_repo
from netsuite.item import item_repo
from netsuite.order import order_service
from netsuite.task import task_service

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
    @pytest.fixture(
        params=[
            "tr1C9m41nQTTWgM4DK37",
        ],
    )
    def order_id(self, request):
        return request.param

    @pytest.mark.parametrize(
        "service",
        [
            order_service.create,
            order_service.close,
        ],
        ids=[
            "create",
            "close",
        ],
    )
    def test_service(self, service, order_id):
        res = service(order_id)
        assert res

    @pytest.mark.parametrize(
        "method",
        [
            "POST",
            "PUT",
        ],
    )
    def test_controller(self, method, order_id):
        res = run("/netsuite/order", {"id": order_id}, method)
        res


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

class TestTask:
    class TestCSVImport:
        @pytest.fixture()
        def body(self):
            with open("test/mocks/Item Demand Plan - import.csv") as f:
                data = f.read()
            return {"id": 544, "data": data}

        def test_service(self, body):
            res = task_service.csv_import_service(body)
            res

        def test_controller(self, body):
            res = run("/netsuite/task/csv_import", {"data": body})
            res

    class TestBankInTransit:
        @pytest.fixture(
            params=[None, "2022-03-22"],
            ids=["auto", "manual"],
        )
        def body(self, request):
            return request.param

        def test_service(self, body):
            res = task_service.bank_in_transit_service(body)
            res

        def test_controller(self, body):
            res = run("/netsuite/task/bank_in_transit", {"data": body})
            res
