from typing import Any
import os
from datetime import datetime
import hashlib
import hmac

import requests
from returns.result import safe

from db.firestore import DB


LAZADA = DB.document("Lazada")


def build_lazada_request(base_url: str, access_token: dict = {}):
    def _build(
        uri: str,
        params: dict[str, Any],
        method: str = "GET",
    ) -> requests.PreparedRequest:
        return requests.Request(
            method,
            url=f"{base_url}{uri}",
            params=sign_params(uri, {**params, **access_token}),
        ).prepare()

    return _build


def sign_params(uri: str, params: dict[str, Any]) -> dict[str, Any]:
    all_params = dict(
        sorted(
            {
                **params,
                "app_key": os.getenv("LAZ_APP_KEY", ""),
                "timestamp": int(datetime.now().timestamp()) * 1000,
                "sign_method": "sha256",
            }.items()
        )
    )
    return {
        **all_params,
        "sign": hmac.new(
            os.getenv("LAZ_APP_SECRET", "").encode("utf-8"),
            (uri + "".join([f"{k}{v}" for k, v in all_params.items()])).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper(),
    }
