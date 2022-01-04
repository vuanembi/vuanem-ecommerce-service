from typing import Any, Callable, Optional
import os
import time
import hashlib
import hmac

import requests

from db.firestore import DB
from lazada import lazada


LAZADA = DB.document("Lazada")


def build_lazada_request(
    base_url: str,
    access_token: Optional[lazada.AccessToken] = None,
) -> Callable[[str, dict[str, Any]], requests.PreparedRequest]:
    def _build(uri: str, params: dict[str, Any]) -> requests.PreparedRequest:
        return requests.Request(
            "GET",
            url=f"{base_url}{uri}",
            params=sign_params(
                uri,
                {
                    **params,
                    "access_token": access_token["access_token"],
                }
                if access_token
                else params,
            ),
        ).prepare()

    return _build


def sign_params(uri: str, params: dict[str, Any]) -> dict[str, Any]:
    all_params = dict(
        sorted(
            {
                **params,
                "app_key": os.getenv("LAZ_APP_KEY", ""),
                "timestamp": int(round(time.time())) * 1000,
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
        )
        .hexdigest()
        .upper(),
    }
