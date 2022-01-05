from returns.pipeline import is_successful
from returns.result import Success
from netsuite import (
    netsuite_service,
    netsuite_repo,
    prepare_repo,
    saved_search_service,
)


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


class TestSavedSearch:
    def test_coupon_code(self):
        res = saved_search_service.coupon_code_ss_service(
            {
                "data": [
                    # "1601-KT-BDU03-KMAT-001",
                    # "1601-KT-BDU03-KMAT-002",
                    # "1601-KT-BDU03-KMAT-002",
                ],
            }
        )
        assert is_successful(res)
