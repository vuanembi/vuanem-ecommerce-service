from returns.pipeline import is_successful
from returns.result import Success
from netsuite import (
    analytics_service,
    netsuite_service,
    netsuite_repo,
    prepare_repo,
)

import pytest

from test.conftest import run


class TestPrepare:
    def test_map_sku_to_item_id(self, netsuite_session):
        res1 = prepare_repo.map_sku_to_item_id(netsuite_session, "1206001016001")
        res2 = prepare_repo.map_sku_to_item_id(netsuite_session, "11111")
        assert res1 == "283790"
        assert res2 is None


class TestNetSuite:
    def test_get_or_create_customer(self, netsuite_session):
        exists_res = netsuite_repo._get_or_create_customer(netsuite_session)(
            netsuite_repo._build_customer_request("HM", "0773314403")
        )
        new_res = netsuite_repo._get_or_create_customer(netsuite_session)(
            netsuite_repo._build_customer_request("Test HM", "07733144031998")
        )
        assert exists_res.unwrap() == 599656
        assert is_successful(new_res)

    def test_build_sales_order_from_prepared(
        self,
        netsuite_session,
        prepared_order,
        netsuite_order,
    ):
        res_prepared = netsuite_repo.build_sales_order_from_prepared(netsuite_session)(
            prepared_order
        )
        res = netsuite_repo.build_sales_order_from_prepared(netsuite_session)(
            netsuite_order
        )
        assert res_prepared.unwrap() == netsuite_order
        assert res.unwrap() == netsuite_order

    def test_create_order_service(self, prepared_order_id):
        res = Success(prepared_order_id).bind(netsuite_service.create_order_service)
        assert res


class TestAnalytics:
    @pytest.fixture()
    def coupon_codes(self):
        return [
            "0122-9KGOI-AGI02-0001",
            "0122-9KGOI-AGI02-0011",
        ]

    def test_coupon_code_analytics_service(self, coupon_codes):
        res = analytics_service.coupon_code_analytics_service({"data": coupon_codes})
        assert is_successful(res)

    def test_coupon_code_ss_service(self, coupon_codes):
        res = analytics_service.coupon_code_ss_service({"data": coupon_codes})
        assert is_successful(res)

    def test_coupon_code_analytics_controller(self, coupon_codes):
        res = run("/netsuite/analytics/coupon_code", {"data": coupon_codes})
        assert res

    def test_coupon_code_controller(self, coupon_codes):
        res = run("/netsuite/saved_search/coupon_code", {"data": coupon_codes})
        assert res
