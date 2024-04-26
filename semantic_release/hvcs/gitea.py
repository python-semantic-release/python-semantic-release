"""Helper code for interacting with a Gitea remote VCS"""

from __future__ import annotations

import glob
import logging
import os
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from requests import HTTPError, JSONDecodeError
from urllib3.util.url import Url, parse_url

from semantic_release.errors import (
    AssetUploadError,
    IncompleteReleaseError,
    UnexpectedResponse,
)
from semantic_release.helpers import logged_function
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session, suppress_not_found

if TYPE_CHECKING:
    from typing import Any, Callable


# Globals
log = logging.getLogger(__name__)


class Gitea(RemoteHvcsBase):
    """Gitea helper class"""

    DEFAULT_DOMAIN = "gitea.com"
    DEFAULT_API_PATH = "/api/v1"
    DEFAULT_ENV_TOKEN_NAME = "GITEA_TOKEN"  # noqa: S105

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
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

        domain_url = self._normalize_url(
            hvcs_domain
            or os.getenv("GITEA_SERVER_URL", "")
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

        self._api_url = self._normalize_url(
            os.getenv("GITEA_API_URL", "").rstrip("/")
            or Url(
                # infer from Domain url and append the default api path
                **{
                    **self.hvcs_domain._asdict(),
                    "path": f"{self.hvcs_domain.path or ''}{self.DEFAULT_API_PATH}",
                }
            ).url,
            allow_insecure=allow_insecure,
        )

    @logged_function(log)
    def create_release(
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,
        assets: list[str] | None = None,
    ) -> int:
        """
        Create a new release

        Ref: https://gitea.com/api/swagger#/repository/repoCreateRelease

        :param tag: Tag to create release for

        :param release_notes: The release notes for this version

        :param prerelease: Whether or not this release should be specified as a
        prerelease

        :return: Whether the request succeeded
        """
        log.info("Creating release for tag %s", tag)
        releases_endpoint = self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases",
        )
        response = self.session.post(
            releases_endpoint,
            json={
                "tag_name": tag,
                "name": tag,
                "body": release_notes,
                "draft": False,
                "prerelease": prerelease,
            },
        )

        # Raise an error if the request was not successful
        response.raise_for_status()

        try:
            release_id: int = response.json()["id"]
            log.info("Successfully created release with ID: %s", release_id)
        except JSONDecodeError as err:
            raise UnexpectedResponse("Unreadable json response") from err
        except KeyError as err:
            raise UnexpectedResponse("JSON response is missing an id") from err

        errors = []
        for asset in assets or []:
            log.info("Uploading asset %s", asset)
            try:
                self.upload_release_asset(release_id, asset)
            except HTTPError as err:
                errors.append(
                    AssetUploadError(f"Failed asset upload for {asset}").with_traceback(
                        err.__traceback__
                    )
                )

        if len(errors) < 1:
            return release_id

        for error in errors:
            log.exception(error)

        raise IncompleteReleaseError(
            f"Failed to upload asset{'s' if len(errors) > 1 else ''} to release!"
        )

    @logged_function(log)
    @suppress_not_found
    def get_release_id_by_tag(self, tag: str) -> int | None:
        """
        Get a release by its tag name
        https://gitea.com/api/swagger#/repository/repoGetReleaseByTag
        :param tag: Tag to get release for
        :return: ID of found release
        """
        tag_endpoint = self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases/tags/{tag}",
        )
        response = self.session.get(tag_endpoint)

        # Raise an error if the request was not successful
        response.raise_for_status()

        try:
            data = response.json()
            return data["id"]
        except JSONDecodeError as err:
            raise UnexpectedResponse("Unreadable json response") from err
        except KeyError as err:
            raise UnexpectedResponse("JSON response is missing an id") from err

    @logged_function(log)
    def edit_release_notes(self, release_id: int, release_notes: str) -> int:
        """
        Edit a release with updated change notes
        https://gitea.com/api/swagger#/repository/repoEditRelease
        :param id: ID of release to update
        :param release_notes: The release notes for this version
        :return: The ID of the release that was edited
        """
        log.info("Updating release %s", release_id)
        release_endpoint = self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases/{release_id}",
        )

        response = self.session.patch(
            release_endpoint,
            json={"body": release_notes},
        )

        # Raise an error if the request was not successful
        response.raise_for_status()

        return release_id

    @logged_function(log)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """
        Post release changelog
        :param version: The version number
        :param changelog: The release notes for this version
        :return: The status of the request
        """
        log.info("Creating release for %s", tag)
        try:
            return self.create_release(tag, release_notes, prerelease)
        except HTTPError as err:
            log.debug("error creating release: %s", err)
            log.debug("looking for an existing release to update")

        release_id = self.get_release_id_by_tag(tag)
        if release_id is None:
            raise ValueError(
                f"release id for tag {tag} not found, and could not be created"
            )

        # If this errors we let it die
        log.debug("Found existing release %s, updating", release_id)
        return self.edit_release_notes(release_id, release_notes)

    @logged_function(log)
    def asset_upload_url(self, release_id: str) -> str:
        """
        Get the correct upload url for a release
        https://gitea.com/api/swagger#/repository/repoCreateReleaseAttachment
        :param release_id: ID of the release to upload to
        """
        return self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases/{release_id}/assets",
        )

    @logged_function(log)
    def upload_release_asset(
        self,
        release_id: int,
        file: str,
        label: str | None = None,  # noqa: ARG002
    ) -> bool:
        """
        Upload an asset to an existing release
        https://gitea.com/api/swagger#/repository/repoCreateReleaseAttachment
        :param release_id: ID of the release to upload to
        :param file: Path of the file to upload
        :param label: this parameter has no effect
        :return: The status of the request
        """
        url = self.asset_upload_url(release_id)

        with open(file, "rb") as attachment:
            name = os.path.basename(file)
            content_type = "application/octet-stream"
            response = self.session.post(
                url,
                params={"name": name},
                data={},
                files={
                    "attachment": (
                        name,
                        attachment,
                        content_type,
                    ),
                },
            )

            # Raise an error if the request was not successful
            response.raise_for_status()

        log.info(
            "Successfully uploaded %s to Gitea, url: %s, status code: %s",
            file,
            response.url,
            response.status_code,
        )

        return True

    @logged_function(log)
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload distributions to a release
        :param tag: Tag to upload for
        :param path: Path to the dist directory
        :return: The number of distributions successfully uploaded
        """
        # Find the release corresponding to this tag
        release_id = self.get_release_id_by_tag(tag=tag)
        if not release_id:
            log.warning("No release corresponds to tag %s, can't upload dists", tag)
            return 0

        # Upload assets
        n_succeeded = 0
        for file_path in (
            f for f in glob.glob(dist_glob, recursive=True) if os.path.isfile(f)
        ):
            try:
                self.upload_release_asset(release_id, file_path)
                n_succeeded += 1
            except HTTPError:  # noqa: PERF203
                log.exception("error uploading asset %s", file_path)

        return n_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            return self._remote_url

        return self.create_server_url(
            auth=self.token,
            path=f"{self.owner}/{self.repo_name}.git",
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_repo_url(repo_path=f"/commit/{commit_hash}")

    def issue_url(self, issue_num: str | int) -> str:
        return self.create_repo_url(repo_path=f"/issues/{issue_num}")

    def pull_request_url(self, pr_number: str | int) -> str:
        return self.create_repo_url(repo_path=f"/pulls/{pr_number}")

    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        return (
            self.create_server_url,
            self.create_repo_url,
            self.commit_hash_url,
            self.issue_url,
            self.pull_request_url,
        )


RemoteHvcsBase.register(Gitea)
