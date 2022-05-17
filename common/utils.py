from typing import Any
from functools import reduce
import time
import csv
import io

from returns.methods import cond
from returns.result import Result


def compose(*func):
    def _compose(f, g):
        return lambda x: f(g(x))

    return reduce(_compose, func, lambda x: x)


def check_expired(token: dict) -> Result[dict, dict]:
    return cond(Result, token["expires_at"] > time.time() + 3600, token, token)


def json_to_csv(data: list[dict[str, Any]]) -> io.BytesIO:
    output_str = io.StringIO()
    cw = csv.DictWriter(output_str, list(data.copy().pop().keys()))
    cw.writerows(data)
    output_str.seek(0)
    return io.BytesIO(output_str.read().encode("utf-8"))
