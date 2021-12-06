import pytest

from libs.firestore import add_prepared_order

def test_add_prepared_order(prepared_order):
    res = add_prepared_order(prepared_order)
    res
