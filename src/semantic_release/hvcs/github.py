"""Helper code for interacting with a GitHub remote VCS"""

from __future__ import annotations

import glob
import mimetypes
import os
from functools import lru_cache
from pathlib import PurePosixPath
from re import compile as regexp
from typing import TYPE_CHECKING

from requests import HTTPError, JSONDecodeError
from urllib3.util.url import Url, parse_url

from semantic_release.cli.util import noop_report
from semantic_release.errors import (
    AssetUploadError,
    IncompleteReleaseError,
    UnexpectedResponse,
)
from semantic_release.globals import logger
from semantic_release.helpers import logged_function
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session, suppress_not_found

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Callable


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
if mimetypes.guess_type("test.whl")[0] != "application/octet-stream":
    mimetypes.add_type("application/octet-stream", ".whl")

if mimetypes.guess_type("test.md")[0] != "text/markdown":
    mimetypes.add_type("text/markdown", ".md")


class Github(RemoteHvcsBase):
    """
    GitHub HVCS interface for interacting with GitHub repositories

    This class supports the following products:

        - GitHub Free, Pro, & Team
        - GitHub Enterprise Cloud
        - GitHub Enterprise Server (on-premises installations)

    This interface does its best to detect which product is configured based
    on the provided domain. If it is the official `github.com`, the default
    domain, then it is considered as GitHub Enterprise Cloud which uses the
    subdomain `api.github.com` for api communication.

    If the provided domain is anything else, than it is assumed to be communicating
    with an on-premise or 3rd-party maintained GitHub instance which matches with
    the GitHub Enterprise Server product. The on-prem server product uses a
    path prefix for handling api requests which is configured to be
    `server.domain/api/v3` based on the documentation in April 2024.
    """

    OFFICIAL_NAME = "GitHub"
    DEFAULT_DOMAIN = "github.com"
    DEFAULT_API_SUBDOMAIN_PREFIX = "api"
    DEFAULT_API_DOMAIN = f"{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}"
    DEFAULT_API_PATH_CLOUD = "/"  # no path prefix!
    DEFAULT_API_PATH_ONPREM = "/api/v3"
    DEFAULT_API_URL_CLOUD = f"https://{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}{DEFAULT_API_PATH_CLOUD}".rstrip(
        "/"
    )
    DEFAULT_ENV_TOKEN_NAME = "GH_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        *,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
        allow_insecure: bool = False,
        **_kwargs: Any,
    ) -> None:
        super().__init__(remote_url)
        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        domain_url_str = (
            hvcs_domain
            or os.getenv("GITHUB_SERVER_URL", "")
            or f"https://{self.DEFAULT_DOMAIN}"
        )

        domain_url = self._normalize_url(
            domain_url_str,
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

        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        api_url_str = (
            hvcs_api_domain
            or os.getenv("GITHUB_API_URL", "")
            or self._derive_api_url_from_base_domain()
        )

        api_domain_parts = self._normalize_url(
            api_url_str,
            allow_insecure=allow_insecure,
        )

        # As GitHub Enterprise Cloud and GitHub Enterprise Server (on-prem) have different api locations
        # lets check what we have been given and set the api url accordingly
        #   NOTE: Github Server (on premise) uses a path prefix '/api/v3' for the api
        #         while GitHub Enterprise Cloud uses a separate subdomain as the base
        is_github_cloud = bool(self.hvcs_domain.url == f"https://{self.DEFAULT_DOMAIN}")

        if (
            is_github_cloud
            and hvcs_api_domain
            and api_domain_parts.url not in Github.DEFAULT_API_URL_CLOUD
        ):
            # Api was provied but is not a subset of the expected one, raise an error
            # we check for a subset because the user may not have provided the full api path
            # but the correct domain.  If they didn't, then we are erroring out here.
            raise ValueError(
                f"Invalid api domain {api_domain_parts.url} for GitHub Enterprise Cloud. "
                f"Expected {Github.DEFAULT_API_URL_CLOUD}."
            )

        # Set the api url to the default cloud one if we are on cloud, otherwise
        # use the verified api domain for a on-prem server
        self._api_url = parse_url(
            Github.DEFAULT_API_URL_CLOUD
            if is_github_cloud
            else Url(
                # Strip any auth, query or fragment from the domain
                scheme=api_domain_parts.scheme,
                host=api_domain_parts.host,
                port=api_domain_parts.port,
                path=str(
                    PurePosixPath(
                        # pass any custom server prefix path but ensure we don't
                        # double up the api path in the case the user provided it
                        str.replace(
                            api_domain_parts.path or "",
                            self.DEFAULT_API_PATH_ONPREM,
                            "",
                        ).lstrip("/")
                        or "/",
                        # apply the on-prem api path
                        self.DEFAULT_API_PATH_ONPREM.lstrip("/"),
                    )
                ),
            ).url.rstrip("/")
        )

    def _derive_api_url_from_base_domain(self) -> Url:
        return parse_url(
            Url(
                # infer from Domain url and prepend the default api subdomain
                **{
                    **self.hvcs_domain._asdict(),
                    "host": self.hvcs_domain.host,
                    "path": str(
                        PurePosixPath(
                            str.lstrip(self.hvcs_domain.path or "", "/") or "/",
                            self.DEFAULT_API_PATH_ONPREM.lstrip("/"),
                        )
                    ),
                }
            ).url.rstrip("/")
        )

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        # Github actions context
        if "GITHUB_REPOSITORY" in os.environ:
            logger.debug("getting repository owner and name from environment variables")
            owner, name = os.environ["GITHUB_REPOSITORY"].rsplit("/", 1)
            return owner, name

        return super()._get_repository_owner_and_name()

    @logged_function(logger)
    def create_release(
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,
        assets: list[str] | None = None,
        noop: bool = False,
    ) -> int:
        """
        Create a new release

        REF: https://docs.github.com/rest/reference/repos#create-a-release

        :param tag: Tag to create release for

        :param release_notes: The release notes for this version

        :param prerelease: Whether or not this release should be created as a prerelease

        :param assets: a list of artifacts to upload to the release

        :return: the ID of the release
        """
        if noop:
            noop_report(
                str.join(
                    " ",
                    [
                        f"would have created a release for tag {tag}",
                        "with the following notes:\n",
                        release_notes,
                    ],
                )
            )
            if assets:
                noop_report(
                    str.join(
                        "\n",
                        [
                            "would have uploaded the following assets to the release:",
                            *assets,
                        ],
                    )
                )
            return -1

        logger.info("Creating release for tag %s", tag)
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
            logger.info("Successfully created release with ID: %s", release_id)
        except JSONDecodeError as err:
            raise UnexpectedResponse("Unreadable json response") from err
        except KeyError as err:
            raise UnexpectedResponse("JSON response is missing an id") from err

        errors = []
        for asset in assets or []:
            logger.info("Uploading asset %s", asset)
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
            logger.exception(error)

        raise IncompleteReleaseError(
            f"Failed to upload asset{'s' if len(errors) > 1 else ''} to release!"
        )

    @logged_function(logger)
    @suppress_not_found
    def get_release_id_by_tag(self, tag: str) -> int | None:
        """
        Get a release by its tag name
        https://docs.github.com/rest/reference/repos#get-a-release-by-tag-name
        :param tag: Tag to get release for
        :return: ID of release, if found, else None
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

    @logged_function(logger)
    def edit_release_notes(self, release_id: int, release_notes: str) -> int:
        """
        Edit a release with updated change notes
        https://docs.github.com/rest/reference/repos#update-a-release
        :param release_id: ID of release to update
        :param release_notes: The release notes for this version
        :return: The ID of the release that was edited
        """
        logger.info("Updating release %s", release_id)
        release_endpoint = self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases/{release_id}",
        )

        response = self.session.post(
            release_endpoint,
            json={"body": release_notes},
        )

        # Raise an error if the update was unsuccessful
        response.raise_for_status()

        return release_id

    @logged_function(logger)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """
        Post release changelog
        :param tag: The version number
        :param release_notes: The release notes for this version
        :param prerelease: Whether or not this release should be created as a prerelease
        :return: The status of the request
        """
        logger.info("Creating release for %s", tag)
        try:
            return self.create_release(tag, release_notes, prerelease)
        except HTTPError as err:
            logger.debug("error creating release: %s", err)
            logger.debug("looking for an existing release to update")

        release_id = self.get_release_id_by_tag(tag)
        if release_id is None:
            raise ValueError(
                f"release id for tag {tag} not found, and could not be created"
            )

        logger.debug("Found existing release %s, updating", release_id)
        # If this errors we let it die
        return self.edit_release_notes(release_id, release_notes)

    @logged_function(logger)
    @suppress_not_found
    def asset_upload_url(self, release_id: str) -> str | None:
        """
        Get the correct upload url for a release
        https://docs.github.com/en/enterprise-server@3.5/rest/releases/releases#get-a-release
        :param release_id: ID of the release to upload to
        :return: URL to upload for a release if found, else None
        """
        # https://docs.github.com/en/enterprise-server@3.5/rest/releases/assets#upload-a-release-asset
        release_url = self.create_api_url(
            endpoint=f"/repos/{self.owner}/{self.repo_name}/releases/{release_id}"
        )

        response = self.session.get(release_url)
        response.raise_for_status()

        try:
            upload_url: str = response.json()["upload_url"]
            return upload_url.replace("{?name,label}", "")
        except JSONDecodeError as err:
            raise UnexpectedResponse("Unreadable json response") from err
        except KeyError as err:
            raise UnexpectedResponse(
                "JSON response is missing a key 'upload_url'"
            ) from err

    @logged_function(logger)
    def upload_release_asset(
        self, release_id: int, file: str, label: str | None = None
    ) -> bool:
        """
        Upload an asset to an existing release
        https://docs.github.com/rest/reference/repos#upload-a-release-asset
        :param release_id: ID of the release to upload to
        :param file: Path of the file to upload
        :param label: Optional custom label for this file
        :return: The status of the request
        """
        url = self.asset_upload_url(release_id)
        if url is None:
            raise ValueError(
                "There is no associated url for uploading asset for release "
                f"{release_id}. Release url: "
                f"{self.api_url}/repos/{self.owner}/{self.repo_name}/releases/{release_id}"
            )

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

            # Raise an error if the upload was unsuccessful
            response.raise_for_status()

        logger.debug(
            "Successfully uploaded %s to Github, url: %s, status code: %s",
            file,
            response.url,
            response.status_code,
        )

        return True

    @logged_function(logger)
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload distributions to a release
        :param tag: Version to upload for
        :param dist_glob: Path to the dist directory
        :return: The number of distributions successfully uploaded
        """
        # Find the release corresponding to this version
        release_id = self.get_release_id_by_tag(tag=tag)
        if not release_id:
            logger.warning("No release corresponds to tag %s, can't upload dists", tag)
            return 0

        # Upload assets
        n_succeeded = 0
        errors = []
        for file_path in (
            f for f in glob.glob(dist_glob, recursive=True) if os.path.isfile(f)
        ):
            try:
                self.upload_release_asset(release_id, file_path)
                n_succeeded += 1
            except HTTPError as err:  # noqa: PERF203
                logger.exception("error uploading asset %s", file_path)
                status_code = (
                    err.response.status_code if err.response is not None else "unknown"
                )
                error_msg = f"Failed to upload asset '{file_path}' to release"
                if status_code != "unknown":
                    error_msg += f" (HTTP {status_code})"
                errors.append(error_msg)

        if errors:
            raise AssetUploadError("\n".join(errors))

        return n_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            logger.info("requested to use token for push but no token set, ignoring...")
            return self._remote_url

        actor = os.getenv("GITHUB_ACTOR", None)
        return self.create_server_url(
            auth=f"{actor}:{self.token}" if actor else self.token,
            path=f"/{self.owner}/{self.repo_name}.git",
        )

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        """
        Get the GitHub comparison link between two version tags.
        :param from_rev: The older version to compare.
        :param to_rev: The newer version to compare.
        :return: Link to view a comparison between the two versions.
        """
        return self.create_repo_url(repo_path=f"/compare/{from_rev}...{to_rev}")

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_repo_url(repo_path=f"/commit/{commit_hash}")

    def issue_url(self, issue_num: str | int) -> str:
        # Strips off any character prefix like '#' that usually exists
        if isinstance(issue_num, str) and (
            match := regexp(r"(\d+)$").search(issue_num)
        ):
            try:
                issue_num = int(match.group(1))
            except ValueError:
                return ""

        if isinstance(issue_num, int):
            return self.create_repo_url(repo_path=f"/issues/{issue_num}")

        return ""

    def pull_request_url(self, pr_number: str | int) -> str:
        # Strips off any character prefix like '#' that usually exists
        if isinstance(pr_number, str) and (
            match := regexp(r"(\d+)$").search(pr_number)
        ):
            try:
                pr_number = int(match.group(1))
            except ValueError:
                return ""

        if isinstance(pr_number, int):
            return self.create_repo_url(repo_path=f"/pull/{pr_number}")

        return ""

    def create_release_url(self, tag: str = "") -> str:
        tag_str = tag.strip()
        tag_path = f"tag/{tag_str}" if tag_str else ""
        return self.create_repo_url(repo_path=f"releases/{tag_path}")

    @staticmethod
    def format_w_official_vcs_name(format_str: str) -> str:
        if "%s" in format_str:
            return format_str % Github.OFFICIAL_NAME

        if "{}" in format_str:
            return format_str.format(Github.OFFICIAL_NAME)

        if "{vcs_name}" in format_str:
            return format_str.format(vcs_name=Github.OFFICIAL_NAME)

        return format_str

    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        return (
            self.create_server_url,
            self.create_repo_url,
            self.commit_hash_url,
            self.compare_url,
            self.issue_url,
            self.pull_request_url,
            self.create_release_url,
            self.format_w_official_vcs_name,
        )


RemoteHvcsBase.register(Github)
