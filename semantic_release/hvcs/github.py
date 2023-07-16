"""
Helper code for interacting with a GitHub remote VCS
"""
from __future__ import annotations

import glob
import logging
import mimetypes
import os
from functools import lru_cache

from requests import HTTPError

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session, suppress_not_found

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


class Github(HvcsBase):
    """Github helper class"""

    DEFAULT_DOMAIN = "github.com"
    DEFAULT_API_DOMAIN = "api.github.com"

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        remote_url: str,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
    ) -> None:
        self._remote_url = remote_url

        # pylint: disable=line-too-long
        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        self.hvcs_domain = hvcs_domain or os.getenv(
            "GITHUB_SERVER_URL", self.DEFAULT_DOMAIN
        ).replace("https://", "")

        # not necessarily prefixed with "api." in the case of a custom domain, so
        # can't just default to "api.github.com"
        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        self.hvcs_api_domain = hvcs_api_domain or os.getenv(
            "GITHUB_API_URL", self.DEFAULT_API_DOMAIN
        ).replace("https://", "")

        self.api_url = f"https://{self.hvcs_api_domain}"

        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        # Github actions context
        if "GITHUB_REPOSITORY" in os.environ:
            log.debug("getting repository owner and name from environment variables")
            owner, name = os.environ["GITHUB_REPOSITORY"].rsplit("/", 1)
            return owner, name
        return super()._get_repository_owner_and_name()

    def compare_url(
        self,
        from_rev: str,
        to_rev: str,
    ) -> str:
        """
        Get the GitHub comparison link between two version tags.
        :param from_rev: The older version to compare.
        :param to_rev: The newer version to compare.
        :return: Link to view a comparison between the two versions.
        """
        return (
            f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/compare/"
            f"{from_rev}...{to_rev}"
        )

    @logged_function(log)
    def create_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """Create a new release
        https://docs.github.com/rest/reference/repos#create-a-release
        :param tag: Tag to create release for
        :param release_notes: The release notes for this version
        :param prerelease: Whether or not this release should be created as a prerelease
        :return: the ID of the release
        """
        log.info("Creating release for tag %s", tag)
        resp = self.session.post(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases",
            json={
                "tag_name": tag,
                "name": tag,
                "body": release_notes,
                "draft": False,
                "prerelease": prerelease,
            },
        )

        release_id: int = resp.json()["id"]  # type: ignore
        log.info("Successfully created release with ID: %s", release_id)
        return release_id

    @logged_function(log)
    @suppress_not_found
    def get_release_id_by_tag(self, tag: str) -> int | None:
        """Get a release by its tag name
        https://docs.github.com/rest/reference/repos#get-a-release-by-tag-name
        :param tag: Tag to get release for
        :return: ID of release, if found, else None
        """
        response = self.session.get(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/tags/{tag}"
        )
        return response.json().get("id")  # type: ignore

    @logged_function(log)
    def edit_release_notes(
        self,
        release_id: int,
        release_notes: str,
    ) -> int:
        """Edit a release with updated change notes
        https://docs.github.com/rest/reference/repos#update-a-release
        :param id: ID of release to update
        :param release_notes: The release notes for this version
        :return: The ID of the release that was edited
        """
        log.info("Updating release %s", release_id)
        self.session.post(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}",
            json={"body": release_notes},
        )
        return release_id

    @logged_function(log)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """Post release changelog
        :param version: The version number
        :param release_notes: The release notes for this version
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

        log.debug("Found existing release %s, updating", release_id)
        # If this errors we let it die
        return self.edit_release_notes(release_id, release_notes)

    @logged_function(log)
    def asset_upload_url(self, release_id: str) -> str:
        """Get the correct upload url for a release
        https://docs.github.com/en/enterprise-server@3.5/rest/releases/releases#get-a-release
        :param release_id: ID of the release to upload to
        :return: URL found to upload for a release
        """
        # https://docs.github.com/en/enterprise-server@3.5/rest/releases/assets#upload-a-release-asset ?
        return f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}/assets"

    @logged_function(log)
    def upload_asset(
        self, release_id: int, file: str, label: str | None = None
    ) -> bool:
        """Upload an asset to an existing release
        https://docs.github.com/rest/reference/repos#upload-a-release-asset
        :param release_id: ID of the release to upload to
        :param file: Path of the file to upload
        :param label: Optional custom label for this file
        :return: The status of the request
        """
        url = self.asset_upload_url(release_id)
        content_type = (
            mimetypes.guess_type(file, strict=False)[0] or "application/octet-stream"
        )

        with open(file, "rb") as data:
            response = self.session.post(
                url,
                params={"name": os.path.basename(file), "label": label},
                headers={
                    "Content-Type": content_type,
                },
                data=data.read(),
            )

        log.debug(
            "Successfully uploaded %s to Github, url: %s, status code: %s",
            file,
            response.url,
            response.status_code,
        )

        return True

    @logged_function(log)
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """Upload distributions to a release
        :param version: Version to upload for
        :param path: Path to the dist directory
        :return: The number of distributions successfully uploaded
        """

        # Find the release corresponding to this version
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
                self.upload_asset(release_id, file_path)
                n_succeeded += 1
            except HTTPError:
                log.error("error uploading asset %s", file_path, exc_info=True)

        return n_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        if not (self.token and use_token):
            log.info("requested to use token for push but no token set, ignoring...")
            return self._remote_url
        actor = os.getenv("GITHUB_ACTOR")
        return (
            f"https://{actor}:{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
            if actor
            else f"https://{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/commit/{commit_hash}"

    def pull_request_url(self, pr_number: str | int) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/issues/{pr_number}"
