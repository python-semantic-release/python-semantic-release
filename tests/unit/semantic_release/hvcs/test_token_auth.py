import pytest
from requests import Request

from semantic_release.hvcs.token_auth import TokenAuth


@pytest.fixture
def example_request():
    return Request(
        "GET",
        url="http://example.com",
        headers={
            "User-Agent": "Python3",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )


def test_token_eq():
    t1 = TokenAuth("foo")
    t2 = TokenAuth("foo")

    assert t1 == t2


def test_token_neq():
    t1 = TokenAuth("foo")
    t2 = TokenAuth("bar")

    assert t1 != t2


def test_call_token_auth_sets_headers(example_request):
    old_headers = example_request.headers.copy()
    old_headers.pop("Authorization", None)
    t1 = TokenAuth("foo")
    new_req = t1(example_request)

    auth_header = new_req.headers.pop("Authorization")
    assert auth_header == "token foo"
    assert new_req.headers == old_headers
    assert new_req.__dict__ == example_request.__dict__
