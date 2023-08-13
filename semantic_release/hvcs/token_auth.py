from requests import PreparedRequest
from requests.auth import AuthBase


class TokenAuth(AuthBase):
    """
    requests Authentication for token based authorization.
    This allows us to attach the Authorization header with
    a token to a session.
    """

    def __init__(self, token: str) -> None:
        self.token = token

    def __eq__(self, other: object) -> bool:
        return self.token == getattr(other, "token", None)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __call__(self, req: PreparedRequest) -> PreparedRequest:
        req.headers["Authorization"] = f"token {self.token}"
        return req
