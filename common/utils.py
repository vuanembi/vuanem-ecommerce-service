from functools import reduce
import time

from returns.methods import cond
from returns.result import Result


def compose(*func):
    def _compose(f, g):
        return lambda x: f(g(x))

    return reduce(_compose, func, lambda x: x)


def check_expired(token: dict) -> Result[dict, dict]:
    return cond(Result, token["expires_at"] > time.time() + 3600, token, token)
