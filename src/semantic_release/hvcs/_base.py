"""Common functionality and interface for interacting with Git remote VCS"""

from __future__ import annotations

import warnings
from abc import ABCMeta, abstractmethod
from functools import lru_cache
from typing import TYPE_CHECKING

from semantic_release.helpers import parse_git_url

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Callable


class HvcsBase(metaclass=ABCMeta):
    """
    Interface for subclasses interacting with a remote vcs environment

    Methods generally have a base implementation are implemented here but
    likely just provide a not-supported message but return gracefully

    This class cannot be instantated directly but must be inherited from
    and implement the designated abstract methods.
    """

    def __init__(self, remote_url: str, *args: Any, **kwargs: Any) -> None:
        self._remote_url = remote_url if parse_git_url(remote_url) else ""
        self._name: str | None = None
        self._owner: str | None = None

    def _not_supported(self: HvcsBase, method_name: str) -> None:
        warnings.warn(
            f"{method_name} is not supported by {type(self).__qualname__}",
            stacklevel=2,
        )

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        """
        Parse the repository's remote url to identify the repository
        owner and name
        """
        parsed_git_url = parse_git_url(self._remote_url)
        return parsed_git_url.namespace, parsed_git_url.repo_name

    @property
    def repo_name(self) -> str:
        if self._name is None:
            _, name = self._get_repository_owner_and_name()
            self._name = name
        return self._name

    @property
    def owner(self) -> str:
        if self._owner is None:
            _owner, _ = self._get_repository_owner_and_name()
            self._owner = _owner
        return self._owner

    @abstractmethod
    def remote_url(self, use_token: bool) -> str:
        """
        Return the remote URL for the repository, including the token for
        authentication if requested by setting the `use_token` parameter to True,
        """
        self._not_supported(self.remote_url.__name__)
        return ""

    @abstractmethod
    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        """
        Return a list of functions that can be used as filters in a Jinja2 template

        ex. filters to convert text to URLs for issues and commits
        """
        self._not_supported(self.get_changelog_context_filters.__name__)
        return ()
