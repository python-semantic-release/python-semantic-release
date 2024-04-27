from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest_lazyfixture import lazy_fixture

from semantic_release.hvcs._base import HvcsBase

from tests.const import EXAMPLE_REPO_NAME, EXAMPLE_REPO_OWNER

if TYPE_CHECKING:
    from typing import Any, Callable


class ArbitraryHvcs(HvcsBase):
    def remote_url(self, use_token: bool) -> str:
        return super().remote_url(use_token)

    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        return super().get_changelog_context_filters()


@pytest.mark.parametrize(
    "remote_url, repo_name",
    [
        (lazy_fixture("example_git_ssh_url"), EXAMPLE_REPO_NAME),
        (lazy_fixture("example_git_https_url"), EXAMPLE_REPO_NAME),
        ("git@my.corp.custom.domain:very_serious/business.git", "business"),
    ],
)
def test_get_repository_owner(remote_url, repo_name):
    client = ArbitraryHvcs(remote_url)
    assert client.repo_name == repo_name


@pytest.mark.parametrize(
    "remote_url, owner",
    [
        (lazy_fixture("example_git_ssh_url"), EXAMPLE_REPO_OWNER),
        (lazy_fixture("example_git_https_url"), EXAMPLE_REPO_OWNER),
        ("git@my.corp.custom.domain:very_serious/business.git", "very_serious"),
    ],
)
def test_get_repository_name(remote_url, owner):
    client = ArbitraryHvcs(remote_url)
    assert client.owner == owner


@pytest.mark.parametrize(
    "bad_url",
    [
        "a" * 25,
        "https://a/b/c/d/.git",
        "https://github.com/wrong",
        "git@gitlab.com/somewhere",
    ],
)
def test_hvcs_parse_error(bad_url):
    client = ArbitraryHvcs(bad_url)
    with pytest.raises(ValueError):
        _ = client.repo_name
    with pytest.raises(ValueError):
        _ = client.owner
