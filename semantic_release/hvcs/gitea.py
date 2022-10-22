import glob
import logging
import mimetypes
import os
from typing import Optional, Tuple, Union

from requests import Session
from urllib3 import Retry

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import (
    build_requests_session,
    suppress_http_error,
    suppress_not_found,
)

logger = logging.getLogger(__name__)

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


class Gitea(HvcsBase):
    """Gitea helper class"""

    DEFAULT_DOMAIN = "gitea.com"
    DEFAULT_API_PATH = "/api/v1"
    DEFAULT_API_DOMAIN = f"{DEFAULT_DOMAIN}{DEFAULT_API_PATH}"

    # pylint: disable=super-init-not-called
    def __init__(
        self,
        remote_url: str,
        hvcs_domain: Optional[str] = None,
        hvcs_api_domain: Optional[str] = None,
        token_var: str = "GITEA_TOKEN",
    ) -> None:

        self._remote_url = remote_url

        self.hvcs_domain = hvcs_domain or os.getenv(
            "GITEA_SERVER_URL", self.DEFAULT_DOMAIN
        ).replace("https://", "")

        self.hvcs_api_domain = hvcs_api_domain or os.getenv(
            "GITEA_API_URL", self.DEFAULT_API_DOMAIN
        ).replace("https://", "")

        self.api_url = f"https://{self.hvcs_api_domain}"

        self.token = os.getenv(token_var)
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

    @logged_function(logger)
    @suppress_http_error
    def check_build_status(self, ref: str) -> bool:
        """Check build status
        https://gitea.com/api/swagger#/repository/repoCreateStatus
        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param ref: The sha1 hash of the commit ref
        :return: Was the build status success?
        """
        url = f"{self.api_url}/repos/{self.owner}/{self.repo_name}/statuses/{ref}"
        response = self.session.get(url)
        data = response.json()
        if isinstance(data, list):
            return data[0].get("status") == "success"
        return data.get("status") == "success"

    @logged_function(logger)
    @suppress_http_error
    def create_release(
        self, tag: str, changelog: str, prerelease: bool = False
    ) -> bool:
        """Create a new release
        https://gitea.com/api/swagger#/repository/repoCreateRelease
        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param tag: Tag to create release for
        :param changelog: The release notes for this version
        :return: Whether the request succeeded
        """
        self.session.post(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases",
            json={
                "tag_name": tag,
                "name": tag,
                "body": changelog,
                "draft": False,
                "prerelease": prerelease,
            },
        )
        return True

    @logged_function(logger)
    @suppress_not_found
    def get_release_id_by_tag(self, tag: str) -> Optional[int]:
        """Get a release by its tag name
        https://gitea.com/api/swagger#/repository/repoGetReleaseByTag
        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param tag: Tag to get release for
        :return: ID of found release
        """
        response = self.session.get(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/tags/{tag}"
        )
        return response.json().get("id")

    @logged_function(logger)
    @suppress_http_error
    def edit_release_changelog(self, release_id: int, changelog: str) -> bool:
        """Edit a release with updated change notes
        https://gitea.com/api/swagger#/repository/repoEditRelease
        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param id: ID of release to update
        :param changelog: The release notes for this version
        :return: Whether the request succeeded
        """
        self.session.patch(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}",
            json={"body": changelog},
        )
        return True

    @logged_function(logger)
    def create_or_update_release(self, tag: str, changelog: str) -> bool:
        """Post release changelog
        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version
        :return: The status of the request
        """
        logger.debug("Attempting to create release for %s", tag)
        success = self.create_release(tag, changelog)

        if not success:
            logger.debug("Unsuccessful, looking for an existing release to update")
            release_id = self.get_release_id_by_tag(tag)
            if release_id:
                logger.debug("Updating release %d", release_id)
                success = self.edit_release_changelog(release_id, changelog)
            else:
                logger.debug("Existing release not found")

        return success

    @logged_function(logger)
    def asset_upload_url(self, release_id: str) -> str:
        """Get the correct upload url for a release
        https://gitea.com/api/swagger#/repository/repoCreateReleaseAttachment
        :param release_id: ID of the release to upload to
        """
        return f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}/assets"

    @logged_function(logger)
    @suppress_http_error
    def upload_asset(
        self, release_id: int, file: str, label: Optional[str] = None
    ) -> bool:
        """Upload an asset to an existing release
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

        logger.debug(
            "Asset upload on Gitea completed, url: %s, status code: %d",
            response.url,
            response.status_code,
        )

        return True

    @logged_function(logger)
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """Upload distributions to a release
        :param tag: Tag to upload for
        :param path: Path to the dist directory
        :return: The number of distributions successfully uploaded
        """

        # Find the release corresponding to this tag
        release_id = self.get_release_id_by_tag(tag=tag)
        if not release_id:
            logger.debug("No release found to upload assets to")
            return False

        # Upload assets
        n_succeeded = 0
        for file_path in (
            f for f in glob.glob(dist_glob, recursive=True) if os.path.isfile(f)
        ):
            n_succeeded += self.upload_asset(release_id, file_path)

        return n_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        if not (self.token and use_token):
            return self._remote_url
        return (
            f"https://{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/commit/{commit_hash}"

    def pull_request_url(self, pr_number: Union[str, int]) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/pulls/{pr_number}"
