from typing import TypedDict

class AccessToken(TypedDict):
    access_token: str
    refresh_token: str
    refresh_expires_in: int
    expires_in: int
    expires_at: int
