from __future__ import annotations

from typing import TYPE_CHECKING

from requests.auth import AuthBase

if TYPE_CHECKING:
    from requests import PreparedRequest


class TokenAuth(AuthBase):
    """
    requests Authentication for token based authorization.
    This allows us to attach the Authorization header with
    a token to a session.
    """

    def __init__(self, token: str, header: str | None = None) -> None:
        """
        Initialize requests Authentication for token based authorization.
        This allows us to attach the Authorization header with
        a token to a session.
        :param token: Authorization token.
        :param header: requests authorization header name.  Valid values
            Authorization - (default) requests Authorization token header.
            PRIVATE-TOKEN - Gitlab REST API private access token Authorization header.
        """
        self.token = token
        self.header = header or "Authorization"

    def __eq__(self, other: object) -> bool:
        return self.token == getattr(other, "token", None)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __call__(self, req: PreparedRequest) -> PreparedRequest:
        # handle Gitlab REST API Private Access Token authorization
        token = self.token if self.header == "PRIVATE-TOKEN" else f"token {self.token}"
        req.headers[self.header] = token
        return req
