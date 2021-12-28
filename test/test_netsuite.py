import pytest

from returns.pipeline import is_successful
from netsuite import netsuite_repo, prepare_repo


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
        res = netsuite_repo.build_sales_order_from_prepared(netsuite_session)(
            prepared_order
        )
        assert res.unwrap() == netsuite_order

    def test_create_sales_order(self, netsuite_session, netsuite_order):
        res = netsuite_repo.create_sales_order(netsuite_session)(netsuite_order)
        assert res
