import logging
import os
from typing import Optional, Tuple

from urllib3 import Retry

from semantic_release.helpers import parse_git_url
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
class HvcsBase:
    def __init__(
        self,
        remote_url: str,
        hvcs_domain: Optional[str] = None,
        hvcs_api_domain: Optional[str] = None,
        token_var: str = "",
    ) -> None:
        self.hvcs_domain = hvcs_domain
        self.hvcs_api_domain = hvcs_api_domain
        self.token = os.getenv(token_var, "")
        auth = TokenAuth(self.token)
        self._remote_url = remote_url
        self.session = build_requests_session(auth=auth)

    def _get_repository_owner_and_name(self) -> Tuple[str, str]:
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
        raise NotImplementedError()

    def upload_dists(self, release_id: str, path: str) -> bool:
        # release_id is generally just the tag
        # Skip on unsupported HVCS instead of raising error
        return True

    def create_release(self, tag: str, changelog: str, prerelease: bool = False) -> bool:
        raise NotImplementedError()

    def get_release_id_by_tag(self, tag: str) -> Optional[int]:
        raise NotImplementedError()

    def edit_release_changelog(self, release_id: int, changelog: str) -> bool:
        raise NotImplementedError()

    def create_or_update_release(
        self, tag: str, changelog: str
    ) -> bool:
        raise NotImplementedError()

    def asset_upload_url(self, release_id: str) -> Optional[str]:
        raise NotImplementedError()

    def upload_asset(self, release_id: int, file: str, label: Optional[str] = None) -> bool:
        raise NotImplementedError()

    def remote_url(self, use_token: bool) -> str:
        raise NotImplementedError()

    def commit_hash_url(self, commit_hash: str) -> str:
        raise NotImplementedError()

    def pull_request_url(self, pr_number: str) -> str:
        raise NotImplementedError()
