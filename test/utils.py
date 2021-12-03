from typing import Optional
from unittest.mock import Mock
from main import main


def run(path: str, data: Optional[dict] = None) -> dict:
    return main(Mock(get_json=Mock(return_value=data), path=path, args=data))
