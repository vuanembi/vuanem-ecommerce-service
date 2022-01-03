from returns.result import Failure
from returns.pipeline import is_successful

import pytest

from lazada import lazada_service, auth_repo


class TestAuth:
    @pytest.fixture()
    def access_token(self):
        return {
            "access_token": "50000801024qApsaa4FtFlqcTRjdEfRhMUzh130a6c91KGPo1iruDg2HThVT8Sko",
            "country": "vn",
            "refresh_token": "50001801824wrksatuCWEeq6MU0jIivKXGwx13b00d54oF2GutbLszvuRoqE88Bd",
            "account_platform": "seller_center",
            "refresh_expires_in": 15552000,
            "country_user_info": [
                {
                    "country": "vn",
                    "user_id": "100553588",
                    "seller_id": "1000277583",
                    "short_code": "VNJ2K34I",
                }
            ],
            "expires_in": 2592000,
            "account": "duong.nguyen3@vuanem.com.vn",
            "code": "0",
            "request_id": "214100f016411257621594163",
            # "expires_at": 1640970000 + 2592000,
            "expires_at": 1640970000 - 2592000,
        }

    def test_get_access_token(self, access_token):
        res = auth_repo.get_access_token().unwrap()
        res


    def test_update_access_token(self, access_token):
        res = auth_repo.update_access_token(access_token)
        res

    def test_refresh_token(self, access_token, session):
        res = auth_repo.refresh_token(session, access_token)
        res

    def test_expired_token(self, access_token, session):
        res = Failure(access_token).lash(lazada_service._update_new_token(session))
        res

    def test_auth_service(self, session):
        res = lazada_service.auth_service(session)
        assert is_successful(res)
