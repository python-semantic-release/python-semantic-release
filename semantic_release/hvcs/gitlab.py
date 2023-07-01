"""
Helper code for interacting with a Gitlab remote VCS
"""
from __future__ import annotations

import logging
import mimetypes
import os
from functools import lru_cache
from urllib.parse import urlsplit

import gitlab

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
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


class Gitlab(HvcsBase):
    """
    Gitlab helper class
    Note Gitlab doesn't really have the concept of a separate
    API domain
    """

    DEFAULT_DOMAIN = "gitlab.com"

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        remote_url: str,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
    ) -> None:
        self._remote_url = remote_url
        self.hvcs_domain = (
            hvcs_domain or self._domain_from_environment() or self.DEFAULT_DOMAIN
        )
        self.hvcs_api_domain = hvcs_api_domain or self.hvcs_domain.replace(
            "https://", ""
        )
        self.api_url = os.getenv("CI_SERVER_URL", f"https://{self.hvcs_api_domain}")

        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

    @staticmethod
    def _domain_from_environment() -> str | None:
        """
        Use Gitlab-CI environment varable to get the server domain, if available
        """
        if "CI_SERVER_URL" in os.environ:
            url = urlsplit(os.environ["CI_SERVER_URL"])
            return f"{url.netloc}{url.path}".rstrip("/")
        return os.getenv("CI_SERVER_HOST")

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        """
        Get the repository owner and name from GitLab CI environment variables, if
        available, otherwise from parsing the remote url
        """
        if "CI_PROJECT_NAMESPACE" in os.environ and "CI_PROJECT_NAME" in os.environ:
            log.debug("getting repository owner and name from environment variables")
            return os.environ["CI_PROJECT_NAMESPACE"], os.environ["CI_PROJECT_NAME"]
        return super()._get_repository_owner_and_name()

    @logged_function(log)
    def create_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> str:
        """Post release changelog
        :param tag: Tag to create release for
        :param release_notes: The release notes for this version
        :param prerelease: This parameter has no effect
        :return: The tag of the release
        """
        client = gitlab.Gitlab(self.api_url, private_token=self.token)
        client.auth()
        log.info("Creating release for %s", tag)
        # ref: https://docs.gitlab.com/ee/api/releases/index.html#create-a-release
        client.projects.get(self.owner + "/" + self.repo_name).releases.create(
            {
                "name": "Release " + tag,
                "tag_name": tag,
                "description": release_notes,
            }
        )
        log.info("Successfully created release for %s", tag)
        return tag

    @logged_function(log)
    def edit_release_notes(self, release_id: str, release_notes: str) -> str:  # type: ignore  # TODO make str types accepted here
        client = gitlab.Gitlab(self.api_url, private_token=self.token)
        client.auth()
        log.info("Updating release %s", release_id)

        client.projects.get(self.owner + "/" + self.repo_name).releases.update(
            release_id,
            {
                "description": release_notes,
            },
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
        except gitlab.GitlabCreateError:
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
        """
        Get the remote url including the token for authentication if requested
        """
        if not (self.token and use_token):
            return self._remote_url
        return f"https://gitlab-ci-token:{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"

    def commit_hash_url(self, commit_hash: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/-/commit/{commit_hash}"

    def pull_request_url(self, pr_number: str | int) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/-/issues/{pr_number}"
