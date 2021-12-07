import os
from functools import reduce

from config import ENV


def compose(*func):
    def _compose(f, g):
        return lambda x: f(g(x))

    return reduce(_compose, func, lambda x: x)


def get_env(key: str):
    return ENV[os.getenv("PYTHON_ENV", "dev")].get(key)
