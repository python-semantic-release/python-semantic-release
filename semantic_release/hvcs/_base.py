"""
Common functionality and interface for interacting with Git remote VCS
"""
from __future__ import annotations

import logging
import warnings
from functools import lru_cache

from semantic_release.helpers import parse_git_url
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session

logger = logging.getLogger(__name__)


# This would be nice as a decorator but it obscured the method's call signature
# which makes mypy unhappy
def _not_supported(self: HvcsBase, method_name: str) -> None:
    warnings.warn(
        f"{method_name} is not supported by {type(self).__qualname__}",
        stacklevel=2,
    )


# pylint: disable=unused-argument
class HvcsBase:
    """
    Interface for subclasses interacting with a remote VCS

    Methods which have a base implementation are implemented here

    Methods which aren't mandatory but should indicate a lack of support gracefully
    (i.e. without raising an exception) return _not_supported, and can be overridden
    to provide an implementation in subclasses. This is more straightforward than
    checking for NotImplemented around every method call.
    """

    def __init__(
        self,
        remote_url: str,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
    ) -> None:
        self.hvcs_domain = hvcs_domain
        self.hvcs_api_domain = hvcs_api_domain
        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self._remote_url = remote_url
        self.session = build_requests_session(auth=auth)

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
        _, _name = self._get_repository_owner_and_name()
        return _name

    @property
    def owner(self) -> str:
        _owner, _ = self._get_repository_owner_and_name()
        return _owner

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        """
        Get the comparison link between two version tags.
        :param from_rev: The older version to compare. Can be a commit sha, tag or branch name.
        :param to_rev: The newer version to compare. Can be a commit sha, tag or branch name.
        :return: Link to view a comparison between the two versions.
        """
        _not_supported(self, "compare_url")
        return ""

    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload built distributions to a release on a remote VCS that
        supports such uploads
        """
        _not_supported(self, "upload_dists")
        return 0

    def create_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int | str:
        """
        Create a release in a remote VCS, if supported
        """
        _not_supported(self, "create_release")
        return -1

    def get_release_id_by_tag(self, tag: str) -> int | None:
        """
        Given a Git tag, return the ID (as the remote VCS defines it) of a corrsponding
        release in the remove VCS, if supported
        """
        _not_supported(self, "get_release_id_by_tag")
        return None

    def edit_release_notes(self, release_id: int, release_notes: str) -> int:
        """
        Edit the changelog associated with a release, if supported
        """
        _not_supported(self, "edit_release_notes")
        return -1

    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int | str:
        """
        Create or update a release for the given tag in a remote VCS, attaching the
        given changelog, if supported
        """
        _not_supported(self, "create_or_update_release")
        return -1

    def asset_upload_url(self, release_id: str) -> str | None:
        """
        Return the URL to use to upload an asset to the given release id, if releases
        are supported by the remote VCS
        """
        _not_supported(self, "asset_upload_url")
        return None

    def upload_asset(
        self, release_id: int, file: str, label: str | None = None
    ) -> bool:
        """
        Upload an asset (file) to a release with the given release_id, if releases are
        supported by the remote VCS. Add a custom label if one is given in the "label"
        parameter and labels are supported by the remote VCS
        """
        _not_supported(self, "upload_asset")
        return True

    def remote_url(self, use_token: bool) -> str:
        """
        Return the remote URL for the repository, including the token for
        authentication if requested by setting the `use_token` parameter to True,
        """
        _not_supported(self, "remote_url")
        return ""

    def commit_hash_url(self, commit_hash: str) -> str:
        """
        Given a commit hash, return a web URL which links to this commit in the
        remote VCS.
        """
        _not_supported(self, "commit_hash_url")
        return ""

    def pull_request_url(self, pr_number: str) -> str:
        """
        Given a number for a PR/Merge request/equivalent, return a web URL that links
        to that PR in the remote VCS.
        """
        _not_supported(self, "pull_request_url")
        return ""
