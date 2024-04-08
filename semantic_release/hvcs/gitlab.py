"""Helper code for interacting with a Gitlab remote VCS"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

import gitlab
from urllib3.util.url import Url, parse_url

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase

if TYPE_CHECKING:
    from typing import Any


# Globals
log = logging.getLogger(__name__)


class Gitlab(HvcsBase):
    """
    Gitlab helper class
    Note Gitlab doesn't really have the concept of a separate
    API domain
    """

    DEFAULT_ENV_TOKEN_NAME = "GITLAB_TOKEN"  # noqa: S105
    # purposefully not CI_JOB_TOKEN as it is not a personal access token,
    # It is missing the permission to push to the repository, but has all others (releases, packages, etc.)

    DEFAULT_DOMAIN = "gitlab.com"

    def __init__(
        self,
        remote_url: str,
        *,
        hvcs_domain: str | None = None,
        token: str | None = None,
        allow_insecure: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(remote_url)
        self._remote_url = remote_url
        self.token = token

        domain_url = parse_url(
            hvcs_domain
            or os.getenv("CI_SERVER_URL", "")
            or f"https://{self.DEFAULT_DOMAIN}"
        )

        if domain_url.scheme == "http" and not allow_insecure:
            raise ValueError("Insecure connections are currently disabled.")

        if not domain_url.scheme:
            new_scheme = "http" if allow_insecure else "https"
            domain_url = Url(**{**domain_url._asdict(), "scheme": new_scheme})

        if domain_url.scheme not in ["http", "https"]:
            raise ValueError(
                f"Invalid scheme {domain_url.scheme} for domain {domain_url.host}. "
                "Only http and https are supported."
            )

        # Strip any auth, query or fragment from the domain
        self.hvcs_domain = parse_url(
            Url(
                scheme=domain_url.scheme,
                host=domain_url.host,
                port=domain_url.port,
                path=str(PurePosixPath(domain_url.path or "/")),
            ).url.rstrip("/")
        )

        self._client = gitlab.Gitlab(self.hvcs_domain.url)

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
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,  # noqa: ARG002
    ) -> str:
        """
        Post release changelog
        :param tag: Tag to create release for
        :param release_notes: The release notes for this version
        :param prerelease: This parameter has no effect
        :return: The tag of the release
        """
        client = gitlab.Gitlab(self.hvcs_domain.url, private_token=self.token)
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

    # TODO: make str types accepted here
    @logged_function(log)
    def edit_release_notes(  # type: ignore[override]
        self,
        release_id: str,
        release_notes: str,
    ) -> str:
        client = gitlab.Gitlab(self.hvcs_domain.url, private_token=self.token)
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
        return self.create_server_url(
            path=f"{self.owner}/{self.repo_name}/-/compare/{from_rev}...{to_rev}"
        )

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            return self._remote_url

        return self.create_server_url(
            auth=f"gitlab-ci-token:{self.token}",
            path=f"{self.owner}/{self.repo_name}.git",
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_server_url(
            path=f"{self.owner}/{self.repo_name}/-/commit/{commit_hash}"
        )

    def issue_url(self, issue_number: str | int) -> str:
        return self.create_server_url(
            path=f"{self.owner}/{self.repo_name}/-/issues/{issue_number}"
        )

    def merge_request_url(self, mr_number: str | int) -> str:
        return self.create_server_url(
            path=f"{self.owner}/{self.repo_name}/-/merge_requests/{mr_number}"
        )

    def pull_request_url(self, pr_number: str | int) -> str:
        return self.merge_request_url(mr_number=pr_number)

    def create_server_url(
        self,
        path: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        overrides = dict(
            filter(
                lambda x: x[1] is not None,
                {
                    "auth": auth,
                    "path": str(PurePosixPath(path or "/")),
                    "query": query,
                    "fragment": fragment,
                }.items(),
            )
        )
        return Url(
            **{
                **self.hvcs_domain._asdict(),
                **overrides,
            }
        ).url.rstrip("/")

    def create_api_url(
        self,
        endpoint: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        api_path = self._client.api_url.replace(self.hvcs_domain.url, "")
        return self.create_server_url(
            path=f"{api_path}/{endpoint.lstrip(api_path)}",
            auth=auth,
            query=query,
            fragment=fragment,
        )
