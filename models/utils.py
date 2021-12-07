from typing import Callable

Response = dict
ResponseBuilder = Callable[[dict], Response]
