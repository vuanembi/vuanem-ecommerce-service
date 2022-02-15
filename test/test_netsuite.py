from returns.pipeline import is_successful
from netsuite import (
    analytics_service,
    netsuite_repo,
    prepare_repo,
)

import pytest
from netsuite.sales_order import sales_order_service

from test.conftest import run


class TestPrepare:
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
        res = prepare_repo.map_sku_to_item_id(netsuite_session, sku)
        assert test_fn(res)


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

    @pytest.mark.parametrize(
        "prepared_order_id",
        [
            "03dbXLxJayed9gbWDvcN",
            "0CM8MOAl8H6VEINaYuIB",
        ],
        ids=[
            "success",
            "fail",
        ],
    )
    def test_create_order_service(self, chat_id, message_id, prepared_order_id):
        res = sales_order_service.create_order_service(
            chat_id,
            message_id,
            prepared_order_id,
        )
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
