"""Helper code for interacting with a Gitlab remote VCS"""
from __future__ import annotations

import logging
import mimetypes
import os
from functools import lru_cache

from requests import PreparedRequest
from requests.auth import AuthBase
from requests.exceptions import HTTPError

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase, _not_supported
from semantic_release.hvcs.util import build_requests_session

log = logging.getLogger(__name__)

# Add a mime type for wheels
# Fix incorrect entries in the `mimetypes` registry.
# On Windows, the Python standard library's `mimetypes` reads in
# mappings from file extension to MIME type from the Windows
# registry. Other applications can and do write incorrect values
# to this registry, which causes `mimetypes.guess_type` to return
# incorrect values, which causes TensorBoard to fail to render on
# the frontend.
# This method hard-codes the correct mappings for certain MIME
# types that are known to be either used by python-semantic-release or
# problematic in general.
mimetypes.add_type("application/octet-stream", ".whl")
mimetypes.add_type("text/markdown", ".md")


class GitlabJobTokenAuth(AuthBase):
    """
    requests Authentication for gitlab job token based authorization.
    This allows us to attach the Authorization header with a token to a session.
    """

    def __init__(self, token: str) -> None:
        self.token = token

    def __eq__(self, other: object) -> bool:
        return self.token == getattr(other, "token", None)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __call__(self, req: PreparedRequest) -> PreparedRequest:
        req.headers["JOB-TOKEN"] = f"{self.token}"
        return req


class GitlabCi(HvcsBase):
    """
    Gitlab helper class
    Note Gitlab doesn't really have the concept of a separate
    API domain
    """

    DEFAULT_ENV_TOKEN_NAME = "CI_JOB_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        hvcs_domain: str | None = None,  # noqa: ARG002
        hvcs_api_domain: str | None = None,  # noqa: ARG002
        token: str | None = None,  # noqa: ARG002
    ) -> None:
        self._remote_url = remote_url
        try:
            self.api_url = os.environ["CI_API_V4_URL"]
            self.hvcs_api_domain = os.environ['CI_SERVER_HOST']
            self.hvcs_domain = os.environ['CI_SERVER_HOST']
            self.project_id = os.environ["CI_PROJECT_ID"]
            self.token = os.environ["CI_JOB_TOKEN"]
            self._get_repository_owner_and_name()
        except KeyError as err:
            raise ValueError("this hvcs type can only run in Gitlab-CI, "
                             "for use outside gitlab-CI please use the gitlab type.") from err

        auth = GitlabJobTokenAuth(self.token)
        self.session = build_requests_session(auth=auth)


    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        """
        Get the repository owner and name from GitLab CI environment variables, if
        available, otherwise from parsing the remote url
        """
        return os.environ["CI_PROJECT_NAMESPACE"], os.environ["CI_PROJECT_NAME"]

    @logged_function(log)
    def create_release(
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,  # noqa: ARG002
    ) -> str:
        """
        Create a new release
        https://docs.gitlab.com/ee/api/releases/index.html#create-a-release
        :param tag: Tag to create release for
        :param release_notes: The release notes for this version
        :param prerelease: This parameter has no effect
        :return: the tag (N.B. the tag is the unique ID of a release for Gitlab)
        """
        log.info("Creating release for tag %s", tag)
        self.session.post(
            f"{self.api_url}/projects/{self.project_id}/releases",
            json={
                "name": "Release " + tag,
                "tag_name": tag,
                "description": release_notes,
            }
        )
        log.info("Successfully created release for: %s", tag)
        return tag

    # TODO: make str types accepted here
    @logged_function(log)
    def edit_release_notes(  # type: ignore[override]
        self,
        release_id: str,
        release_notes: str,
    ) -> str:
        """
        Edit a release with updated change notes
        https://docs.github.com/rest/reference/repos#update-a-release
        :param release_id: tag of the release
        :param release_notes: The release notes for this version
        :return: The tag of the release that was edited.
        """
        log.info("Updating release %s", release_id)
        self.session.put(
            f"{self.api_url}/projects/{self.project_id}/releases/{release_id}",
            json={"description": release_notes},
        )
        return release_id

    @logged_function(log)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> str:
        try:
            return self.create_release(
                tag=tag, release_notes=release_notes, prerelease=prerelease
            )
        except HTTPError:
            # POSSIBLE IMPROVEMENT: Could check that it is indeed because the tag existed.
            log.info(
                "Release %s could not be created for project %s/%s",
                tag,
                self.owner,
                self.repo_name,
            )
            return self.edit_release_notes(release_id=tag, release_notes=release_notes)

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/-/compare/{from_rev}...{to_rev}"

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            return self._remote_url
        _not_supported(self, "remote_url with use_token set to True")
        return self._remote_url

    def commit_hash_url(self, commit_hash: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/-/commit/{commit_hash}"

    def pull_request_url(self, pr_number: str | int) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/-/issues/{pr_number}"
