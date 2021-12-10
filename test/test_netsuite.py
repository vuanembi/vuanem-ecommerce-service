import pytest

from libs.netsuite import (
    map_sku_to_item_id,
    get_customer_if_not_exist,
    create_sales_order,
    build_customer_request,
    build_sales_order_from_prepared,
)


@pytest.fixture()
def customer():
    return build_customer_request("HM", "1900561252")


def test_get_customer(oauth_session, customer):
    res = get_customer_if_not_exist(oauth_session, customer)
    assert res


def test_map_sku_to_item_id(oauth_session):
    assert map_sku_to_item_id(oauth_session, "1206001016001") == "283790"
    assert map_sku_to_item_id(oauth_session, "1206001016001123123") is None


def test_build_sales_order_from_prepared(oauth_session, prepared_order, netsuite_order):
    assert (
        build_sales_order_from_prepared(oauth_session, prepared_order) == netsuite_order
    )


def test_create_sales_order(oauth_session, netsuite_order):
    res = create_sales_order(oauth_session, netsuite_order)
    assert res
