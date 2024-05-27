"""Helper code for interacting with a Gitlab remote VCS"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

import gitlab
import gitlab.exceptions
import gitlab.v4
import gitlab.v4.objects
from urllib3.util.url import Url, parse_url

from semantic_release.errors import UnexpectedResponse
from semantic_release.helpers import logged_function
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.hvcs.util import suppress_not_found

if TYPE_CHECKING:
    from typing import Any, Callable

    from gitlab.v4.objects import Project as GitLabProject


log = logging.getLogger(__name__)


# Globals
log = logging.getLogger(__name__)


class Gitlab(RemoteHvcsBase):
    """Gitlab HVCS interface for interacting with Gitlab repositories"""

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
        self.token = token
        self.project_namespace = f"{self.owner}/{self.repo_name}"
        self._project: GitLabProject | None = None

        domain_url = self._normalize_url(
            hvcs_domain
            or os.getenv("CI_SERVER_URL", "")
            or f"https://{self.DEFAULT_DOMAIN}",
            allow_insecure=allow_insecure,
        )

        # Strip any auth, query or fragment from the domain
        self._hvcs_domain = parse_url(
            Url(
                scheme=domain_url.scheme,
                host=domain_url.host,
                port=domain_url.port,
                path=str(PurePosixPath(domain_url.path or "/")),
            ).url.rstrip("/")
        )

        self._client = gitlab.Gitlab(self.hvcs_domain.url, private_token=self.token)
        self._api_url = parse_url(self._client.api_url)

    @property
    def project(self) -> GitLabProject:
        if self._project is None:
            self._project = self._client.projects.get(self.project_namespace)
        return self._project

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
        assets: list[str] | None = None,  # noqa: ARG002
    ) -> str:
        """
        Create a release in a remote VCS, adding any release notes and assets to it

        Arguments:
        ---------
            tag(str): The tag to create the release for
            release_notes(str): The changelog description for this version only
            prerelease(bool): This parameter has no effect in GitLab
            assets(list[str]): A list of paths to files to upload as assets (TODO: not implemented)

        Returns:
        -------
            str: The tag of the release

        Raises:
        ------
            GitlabAuthenticationError: If authentication is not correct
            GitlabCreateError: If the server cannot perform the request

        """
        log.info("Creating release for %s", tag)
        # ref: https://docs.gitlab.com/ee/api/releases/index.html#create-a-release
        self.project.releases.create(
            {
                "name": tag,
                "tag_name": tag,
                "tag_message": tag,
                "description": release_notes,
            }
        )
        log.info("Successfully created release for %s", tag)
        return tag

    @logged_function(log)
    @suppress_not_found
    def get_release_by_tag(self, tag: str) -> gitlab.v4.objects.ProjectRelease | None:
        """
        Get a release by its tag name

        Arguments:
        ---------
            tag(str): The tag name to get the release for

        Returns:
        -------
            gitlab.v4.objects.ProjectRelease | None: The release object or None if not found

        Raises:
        ------
            gitlab.exceptions.GitlabAuthenticationError: If the user is not authenticated

        """
        try:
            return self.project.releases.get(tag)
        except gitlab.exceptions.GitlabGetError:
            log.debug("Release %s not found", tag)
            return None
        except KeyError as err:
            raise UnexpectedResponse("JSON response is missing commit.id") from err

    @logged_function(log)
    def edit_release_notes(  # type: ignore[override]
        self,
        release: gitlab.v4.objects.ProjectRelease,
        release_notes: str,
    ) -> str:
        """
        Update the release notes for a given release

        Arguments:
        ---------
            release(gitlab.v4.objects.ProjectRelease): The release object to update
            release_notes(str): The new release notes

        Returns:
        -------
            str: The release id

        Raises:
        ------
            GitlabAuthenticationError: If authentication is not correct
            GitlabUpdateError: If the server cannot perform the request

        """
        log.info(
            "Updating release %s [%s]",
            release.name,
            release.attributes.get("commit", {}).get("id"),
        )
        release.description = release_notes
        release.save()
        return str(release.get_id())

    @logged_function(log)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> str:
        """
        Create or update a release for the given tag in a remote VCS

        Arguments:
        ---------
            tag(str): The tag to create or update the release for
            release_notes(str): The changelog description for this version only
            prerelease(bool): This parameter has no effect in GitLab

        Returns:
        -------
            str: The release id

        Raises:
        ------
            ValueError: If the release could not be created or updated
            gitlab.exceptions.GitlabAuthenticationError: If the user is not authenticated
            GitlabUpdateError: If the server cannot perform the request

        """
        try:
            return self.create_release(
                tag=tag, release_notes=release_notes, prerelease=prerelease
            )
        except gitlab.GitlabCreateError:
            log.info(
                "New release %s could not be created for project %s",
                tag,
                self.project_namespace,
            )

        if (release_obj := self.get_release_by_tag(tag)) is None:
            raise ValueError(
                f"release for tag {tag} could not be found, and could not be created"
            )

        log.debug(
            "Found existing release commit %s, updating", release_obj.commit.get("id")
        )
        # If this errors we let it die
        return self.edit_release_notes(
            release=release_obj,
            release_notes=release_notes,
        )

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            return self._remote_url

        return self.create_server_url(
            auth=f"gitlab-ci-token:{self.token}",
            path=f"{self.project_namespace}.git",
        )

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        return self.create_repo_url(repo_path=f"/-/compare/{from_rev}...{to_rev}")

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_repo_url(repo_path=f"/-/commit/{commit_hash}")

    def issue_url(self, issue_number: str | int) -> str:
        return self.create_repo_url(repo_path=f"/-/issues/{issue_number}")

    def merge_request_url(self, mr_number: str | int) -> str:
        return self.create_repo_url(repo_path=f"/-/merge_requests/{mr_number}")

    def pull_request_url(self, pr_number: str | int) -> str:
        # TODO: deprecate in v11, add warning in v10
        return self.merge_request_url(mr_number=pr_number)

    def upload_dists(self, tag: str, dist_glob: str) -> int:
        return super().upload_dists(tag, dist_glob)

    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        return (
            self.create_server_url,
            self.create_repo_url,
            self.commit_hash_url,
            self.compare_url,
            self.issue_url,
            self.merge_request_url,
            self.pull_request_url,
        )


RemoteHvcsBase.register(Gitlab)
