from returns.result import Failure
from returns.pipeline import is_successful

import pytest

from shopee import shopee_service, auth_repo

from test.conftest import run


class TestAuth:
    def test_get_access_token(self, session):
        res = auth_repo.get_access_token(session, "57464249794a64714977477a4b414c68")
        res

    def test_refresh_access_token(self, session):
        res = auth_repo.refresh_access_token(
            session,
            {
                "refresh_token": "5748426a7877766343674f51594b786b",
            },
        )
        res

    def test_auth_service(self):
        res = shopee_service.auth_service()
        res


class TestData:
    pass


class TestIntegration:
    pass
