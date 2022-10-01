from typing import Any

from requests import Request
from requests.auth import AuthBase


class TokenAuth(AuthBase):
    """
    requests Authentication for token based authorization
    """

    def __init__(self, token: str) -> None:
        self.token = token

    def __eq__(self, other: Any) -> bool:
        return self.token == getattr(other, "token", None)

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __call__(self, req: Request) -> Request:
        req.headers["Authorization"] = f"token {self.token}"
        return req
