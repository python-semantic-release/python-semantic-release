"""
Common functionality and interface for interacting with Git remote VCS
"""
import logging
import os
from typing import Optional, Tuple

from semantic_release.helpers import parse_git_url
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
class HvcsBase:
    """
    Interface for subclasses interacting with a remote VCS
    """

    def __init__(
        self,
        remote_url: str,
        hvcs_domain: Optional[str] = None,
        hvcs_api_domain: Optional[str] = None,
        token_var: str = "",
    ) -> None:
        self.hvcs_domain = hvcs_domain
        self.hvcs_api_domain = hvcs_api_domain
        self.token = os.getenv(token_var)
        auth = None if not self.token else TokenAuth(self.token)
        self._remote_url = remote_url
        self.session = build_requests_session(auth=auth)

    def _get_repository_owner_and_name(self) -> Tuple[str, str]:
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
        raise NotImplementedError()

    def check_build_status(self, ref: str) -> bool:
        """
        Check the status of a build at `ref` in a remote VCS that reports build
        statuses, such as GitHub Actions or GitLab CI
        """
        raise NotImplementedError()

    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload built distributions to a release on a remote VCS that
        supports such uploads
        """
        # release_id is generally just the tag
        # Skip on unsupported HVCS instead of raising error
        return 0

    def create_release(
        self, tag: str, changelog: str, prerelease: bool = False
    ) -> bool:
        """
        Create a release in a remote VCS, if supported
        """
        raise NotImplementedError()

    def get_release_id_by_tag(self, tag: str) -> Optional[int]:
        """
        Given a Git tag, return the ID (as the remote VCS defines it) of a corrsponding
        release in the remove VCS, if supported
        """
        raise NotImplementedError()

    def edit_release_changelog(self, release_id: int, changelog: str) -> bool:
        """
        Edit the changelog associated with a release, if supported
        """
        raise NotImplementedError()

    def create_or_update_release(self, tag: str, changelog: str) -> bool:
        """
        Create or update a release for the given tag in a remote VCS, attaching the
        given changelog, if supported
        """
        raise NotImplementedError()

    def asset_upload_url(self, release_id: str) -> Optional[str]:
        """
        Return the URL to use to upload an asset to the given release id, if releases
        are supported by the remote VCS
        """
        raise NotImplementedError()

    def upload_asset(
        self, release_id: int, file: str, label: Optional[str] = None
    ) -> bool:
        """
        Upload an asset (file) to a release with the given release_id, if releases are
        supported by the remote VCS. Add a custom label if one is given in the "label"
        parameter and labels are supported by the remote VCS
        """
        raise NotImplementedError()

    def remote_url(self, use_token: bool) -> str:
        """
        Return the remote URL for the repository, including the token for
        authentication if requested by setting the `use_token` parameter to True,
        """
        raise NotImplementedError()

    def commit_hash_url(self, commit_hash: str) -> str:
        """
        Given a commit hash, return a web URL which links to this commit in the
        remote VCS.
        """
        raise NotImplementedError()

    def pull_request_url(self, pr_number: str) -> str:
        """
        Given a number for a PR/Merge request/equivalent, return a web URL that links
        to that PR in the remote VCS.
        """
        raise NotImplementedError()
