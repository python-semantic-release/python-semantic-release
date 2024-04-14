"""Helper code for interacting with a GitHub remote VCS"""

from __future__ import annotations

import glob
import logging
import mimetypes
import os
from functools import lru_cache
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from requests import HTTPError, JSONDecodeError
from urllib3.util.url import Url, parse_url

from semantic_release.errors import UnexpectedResponse
from semantic_release.helpers import logged_function
from semantic_release.hvcs._base import HvcsBase
from semantic_release.hvcs.token_auth import TokenAuth
from semantic_release.hvcs.util import build_requests_session, suppress_not_found

if TYPE_CHECKING:
    from typing import Any


# Globals
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
if mimetypes.guess_type("test.whl")[0] != "application/octet-stream":
    mimetypes.add_type("application/octet-stream", ".whl")

if mimetypes.guess_type("test.md")[0] != "text/markdown":
    mimetypes.add_type("text/markdown", ".md")


class Github(HvcsBase):
    """
    GitHub HVCS interface for interacting with GitHub repositories

    This class supports the following products:
        - GitHub Free, Pro, & Team
        - GitHub Enterprise Cloud

    This class does not support the following products:
        - GitHub Enterprise Server (on-premises installations)
    """

    # TODO: Add support for GitHub Enterprise Server (on-premises installations)
    #       DEFAULT_ONPREM_API_PATH = "/api/v3"
    DEFAULT_DOMAIN = "github.com"
    DEFAULT_API_SUBDOMAIN_PREFIX = "api"
    DEFAULT_API_DOMAIN = f"{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}"
    DEFAULT_ENV_TOKEN_NAME = "GH_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        *,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
        allow_insecure: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(remote_url)
        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        domain_url = parse_url(
            hvcs_domain
            or os.getenv("GITHUB_SERVER_URL", "")
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

        # ref: https://docs.github.com/en/actions/reference/environment-variables#default-environment-variables
        api_domain_parts = parse_url(
            hvcs_api_domain
            or os.getenv("GITHUB_API_URL", "")
            or Url(
                # infer from Domain url and prepend the default api subdomain
                **{
                    **self.hvcs_domain._asdict(),
                    "host": f"{self.DEFAULT_API_SUBDOMAIN_PREFIX}.{self.hvcs_domain.host}",
                    "path": "",
                }
            ).url
        )

        if api_domain_parts.scheme == "http" and not allow_insecure:
            raise ValueError("Insecure connections are currently disabled.")

        if not api_domain_parts.scheme:
            new_scheme = "http" if allow_insecure else "https"
            api_domain_parts = Url(
                **{**api_domain_parts._asdict(), "scheme": new_scheme}
            )

        if api_domain_parts.scheme not in ["http", "https"]:
            raise ValueError(
                f"Invalid scheme {api_domain_parts.scheme} for api domain {api_domain_parts.host}. "
                "Only http and https are supported."
            )

        # Strip any auth, query or fragment from the domain
        self.api_url = parse_url(
            Url(
                scheme=api_domain_parts.scheme,
                host=api_domain_parts.host,
                port=api_domain_parts.port,
                path=str(PurePosixPath(api_domain_parts.path or "/")),
            ).url.rstrip("/")
        )

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        # Github actions context
        if "GITHUB_REPOSITORY" in os.environ:
            log.debug("getting repository owner and name from environment variables")
            owner, name = os.environ["GITHUB_REPOSITORY"].rsplit("/", 1)
            return owner, name

        return super()._get_repository_owner_and_name()

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        """
        Get the GitHub comparison link between two version tags.
        :param from_rev: The older version to compare.
        :param to_rev: The newer version to compare.
        :return: Link to view a comparison between the two versions.
        """
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/compare/{from_rev}...{to_rev}"
        )

    @logged_function(log)
    def create_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """
        Create a new release
        https://docs.github.com/rest/reference/repos#create-a-release
        :param tag: Tag to create release for
        :param release_notes: The release notes for this version
        :param prerelease: Whether or not this release should be created as a prerelease
        :return: the ID of the release
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
            return release_id
        except JSONDecodeError as err:
            raise UnexpectedResponse("Unreadable json response") from err
        except KeyError as err:
            raise UnexpectedResponse("JSON response is missing an id") from err

    @logged_function(log)
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

    @logged_function(log)
    def edit_release_notes(self, release_id: int, release_notes: str) -> int:
        """
        Edit a release with updated change notes
        https://docs.github.com/rest/reference/repos#update-a-release
        :param id: ID of release to update
        :param release_notes: The release notes for this version
        :return: The ID of the release that was edited
        """
        log.info("Updating release %s", release_id)
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

    @logged_function(log)
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int:
        """
        Post release changelog
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

    @logged_function(log)
    def upload_asset(
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

        log.debug(
            "Successfully uploaded %s to Github, url: %s, status code: %s",
            file,
            response.url,
            response.status_code,
        )

        return True

    @logged_function(log)
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload distributions to a release
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
            except HTTPError:  # noqa: PERF203
                log.exception("error uploading asset %s", file_path)

        return n_succeeded

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not (self.token and use_token):
            log.info("requested to use token for push but no token set, ignoring...")
            return self._remote_url

        actor = os.getenv("GITHUB_ACTOR", None)
        return self.create_server_url(
            auth=f"{actor}:{self.token}" if actor else self.token,
            path=f"/{self.owner}/{self.repo_name}.git",
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/commit/{commit_hash}"
        )

    def pull_request_url(self, pr_number: str | int) -> str:
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/issues/{pr_number}"
        )

    def _derive_url(
        self,
        base_url: Url,
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
                    "path": str(PurePosixPath("/", path)),
                    "query": query,
                    "fragment": fragment,
                }.items(),
            )
        )
        return Url(
            **{
                **base_url._asdict(),
                **overrides,
            }
        ).url.rstrip("/")

    def create_server_url(
        self,
        path: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        return self._derive_url(self.hvcs_domain, path, auth, query, fragment)

    def create_api_url(
        self,
        endpoint: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        return self._derive_url(self.api_url, endpoint, auth, query, fragment)
