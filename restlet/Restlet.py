from typing import TypedDict, Optional, Protocol
from collections import OrderedDict

from requests_oauthlib import OAuth1Session


class Restlet(TypedDict):
    script: int
    deploy: int


class RestletRequest(Protocol):
    def __call__(
        self,
        session: OAuth1Session,
        method: str,
        params: dict = {},
        body: Optional[OrderedDict] = None,
    ) -> dict:
        pass
