import logging
import mimetypes
import os
from typing import Optional, Union, Tuple

from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase
from semantic_release.hvcs.util import (
    suppress_http_error,
    suppress_not_found,
    build_requests_session,
)
from semantic_release.hvcs.token_auth import TokenAuth


logger = logging.getLogger(__name__)

# Add a mime type for wheels
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
        hvcs_domain: Optional[str] = None,
        hvcs_api_domain: Optional[str] = None,
        token_var: str = "GH_TOKEN",
    ) -> None:

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

        self.token = os.getenv(token_var)
        auth = None if not self.token else TokenAuth(self.token)
        self._remote_url = remote_url
        self.session = build_requests_session(auth=auth)

    def _get_repository_owner_and_name(self) -> Tuple[str, str]:
        # Github actions context
        if "GITHUB_REPOSITORY" in os.environ:
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

    @logged_function(logger)
    @suppress_http_error
    def check_build_status(self, ref: str) -> bool:
        """Check build status
        https://docs.github.com/rest/reference/repos#get-the-combined-status-for-a-specific-reference
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param ref: The sha1 hash of the commit ref
        :return: Was the build status success?
        """
        url = f"{self.api_url}/repos/{self.owner}/{self.repo_name}/commits/{ref}/status"
        response = self.session.get(url)
        return response.json().get("state") == "success"

    @logged_function(logger)
    @suppress_http_error
    def create_release(
        self, tag: str, changelog: str, prerelease: bool = False
    ) -> bool:
        """Create a new release
        https://docs.github.com/rest/reference/repos#create-a-release
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
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
        https://docs.github.com/rest/reference/repos#get-a-release-by-tag-name
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param tag: Tag to get release for
        :return: ID of found release
        """
        response = self.session.get(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/tags/{tag}"
        )
        return response.json().get("id")

    @logged_function(logger)
    @suppress_http_error
    def edit_release_changelog(
        self,
        release_id: int,
        changelog: str,
    ) -> bool:
        """Edit a release with updated change notes
        https://docs.github.com/rest/reference/repos#update-a-release
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param id: ID of release to update
        :param changelog: The release notes for this version
        :return: Whether the request succeeded
        """
        self.session.post(
            f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}",
            json={"body": changelog},
        )
        return True

    @logged_function(logger)
    def create_or_update_release(self, tag: str, changelog: str) -> bool:
        """Post release changelog
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
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
        https://docs.github.com/en/enterprise-server@3.5/rest/releases/releases#get-a-release
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param release_id: ID of the release to upload to
        :return: URL found to upload for a release
        """
        # https://docs.github.com/en/enterprise-server@3.5/rest/releases/assets#upload-a-release-asset ?
        return f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}/assets"

    @logged_function(logger)
    @suppress_http_error
    def upload_asset(self, release_id: int, file: str, label: str = None) -> bool:
        """Upload an asset to an existing release
        https://docs.github.com/rest/reference/repos#upload-a-release-asset
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param release_id: ID of the release to upload to
        :param file: Path of the file to upload
        :param label: Custom label for this file
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

        logger.debug(
            "Asset upload on Github completed, url: %s, status code: %d",
            response.url,
            response.status_code,
        )

        return True

    @logged_function(logger)
    def upload_dists(self, tag: str, path: str) -> bool:
        """Upload distributions to a release
        :param owner: The owner namespace of the repository
        :param repo_name The repository name
        :param version: Version to upload for
        :param path: Path to the dist directory
        :return: The status of the request
        """

        # Find the release corresponding to this version
        release_id = self.get_release_id_by_tag(ref=tag)
        if not release_id:
            logger.debug("No release found to upload assets to")
            return False

        # Upload assets
        all_succeeded = True
        for file_path in (
            os.path.join(path, file)
            for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file))
        ):
            all_succeeded &= self.upload_asset(release_id, file_path)

        return all_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        if not (self.token and use_token):
            return self._remote_url
        actor = os.getenv("GITHUB_ACTOR")
        return (
            f"https://{actor}:{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
            if actor
            else f"https://{self.token}@{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/commit/{commit_hash}"

    def pull_request_url(self, pr_number: Union[str, int]) -> str:
        return f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/issues/{pr_number}"
