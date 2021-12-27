import pytest

from netsuite import netsuite_repo, prepare_repo


@pytest.fixture()
def customer_req():
    return prepare_repo.build_customer_request("HM", "1900561252")


class TestNetSuitePrepare:
    def test_map_sku_to_item_id(self, oauth_session):
        res1 = prepare_repo.map_sku_to_item_id(oauth_session, "1206001016001")
        res2 = prepare_repo.map_sku_to_item_id(oauth_session, "11111")
        assert res1 == "283790"
        assert res2 is None


class TestNetSuite:
    def test_get_customer(oauth_session, customer_req):
        res = netsuite_repo.get_customer_if_not_exist(oauth_session, customer_req)
        assert res

    def test_build_sales_order_from_prepared(
        oauth_session,
        prepared_order,
        netsuite_order,
    ):
        assert (
            netsuite_repo.build_sales_order_from_prepared(oauth_session, prepared_order)
            == netsuite_order
        )

    def test_create_sales_order(oauth_session, netsuite_order):
        res = netsuite_repo.create_sales_order(oauth_session, netsuite_order)
        assert res
