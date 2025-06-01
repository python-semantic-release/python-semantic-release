"""Helper code for interacting with a Bitbucket remote VCS"""

# Note: Bitbucket doesn't support releases. But it allows users to use
# `semantic-release version` without having to specify `--no-vcs-release`.

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import PurePosixPath
from re import compile as regexp
from typing import TYPE_CHECKING

from urllib3.util.url import Url, parse_url

from semantic_release.globals import logger
from semantic_release.hvcs.remote_hvcs_base import RemoteHvcsBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Callable


class Bitbucket(RemoteHvcsBase):
    """
    Bitbucket HVCS interface for interacting with BitBucket repositories

    This class supports the following products:

        - BitBucket Cloud
        - BitBucket Data Center Server (on-premises installations)

    This interface does its best to detect which product is configured based
    on the provided domain. If it is the official `bitbucket.org`, the default
    domain, then it is considered as BitBucket Cloud which uses the subdomain
    `api.bitbucket.org/2.0` for api communication.

    If the provided domain is anything else, than it is assumed to be communicating
    with an on-premise or 3rd-party maintained BitBucket instance which matches with
    the BitBucket Data Center Server product. The on-prem server product uses a
    path prefix for handling api requests which is configured to be
    `server.domain/rest/api/1.0` based on the documentation in April 2024.
    """

    OFFICIAL_NAME = "Bitbucket"
    DEFAULT_DOMAIN = "bitbucket.org"
    DEFAULT_API_SUBDOMAIN_PREFIX = "api"
    DEFAULT_API_PATH_CLOUD = "/2.0"
    DEFAULT_API_PATH_ONPREM = "/rest/api/1.0"
    DEFAULT_API_URL_CLOUD = f"https://{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}{DEFAULT_API_PATH_CLOUD}"
    DEFAULT_ENV_TOKEN_NAME = "BITBUCKET_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        *,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
        allow_insecure: bool = False,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        super().__init__(remote_url)
        self.token = token
        # NOTE: Uncomment in the future when we actually have functionalty to
        #       use the api, but currently there is none.
        # auth = None if not self.token else TokenAuth(self.token)
        # self.session = build_requests_session(auth=auth)

        domain_url = self._normalize_url(
            hvcs_domain or f"https://{self.DEFAULT_DOMAIN}",
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

        # Parse api domain if provided otherwise infer from domain
        api_domain_parts = self._normalize_url(
            hvcs_api_domain or self._derive_api_url_from_base_domain(),
            allow_insecure=allow_insecure,
        )

        # As Bitbucket Cloud and Bitbucket Server (on-prem) have different api paths
        # lets check what we have been given and set the api url accordingly
        #   ref: https://developer.atlassian.com/server/bitbucket/how-tos/command-line-rest/
        #   NOTE: BitBucket Server (on premise) uses a path prefix '/rest/api/1.0' for the api
        #         while BitBucket Cloud uses a separate subdomain with '/2.0' path prefix
        is_bitbucket_cloud = bool(
            self.hvcs_domain.url == f"https://{self.DEFAULT_DOMAIN}"
        )

        if (
            is_bitbucket_cloud
            and hvcs_api_domain
            and api_domain_parts.url not in Bitbucket.DEFAULT_API_URL_CLOUD
        ):
            # Api was provied but is not a subset of the expected one, raise an error
            # we check for a subset because the user may not have provided the full api path
            # but the correct domain.  If they didn't, then we are erroring out here.
            raise ValueError(
                f"Invalid api domain {api_domain_parts.url} for BitBucket Cloud. "
                f"Expected {Bitbucket.DEFAULT_API_URL_CLOUD}."
            )

        # Set the api url to the default cloud one if we are on cloud, otherwise
        # use the verified api domain for a on-prem server
        self._api_url = parse_url(
            Bitbucket.DEFAULT_API_URL_CLOUD
            if is_bitbucket_cloud
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
                # infer from Domain url and append the api path
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
        # ref: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        if "BITBUCKET_REPO_FULL_NAME" in os.environ:
            logger.info("Getting repository owner and name from environment variables.")
            owner, name = os.environ["BITBUCKET_REPO_FULL_NAME"].rsplit("/", 1)
            return owner, name

        return super()._get_repository_owner_and_name()

    def remote_url(self, use_token: bool = True) -> str:
        """Get the remote url including the token for authentication if requested"""
        if not use_token:
            return self._remote_url

        if not self.token:
            raise ValueError("Requested to use token but no token set.")

        # If the user is set, assume the token is an user secret. This will work
        # on any repository the user has access to.
        # https://support.atlassian.com/bitbucket-cloud/docs/push-back-to-your-repository
        # If the user variable is not set, assume it is a repository token
        # which will only work on the repository it was created for.
        # https://support.atlassian.com/bitbucket-cloud/docs/using-access-tokens
        user = os.environ.get("BITBUCKET_USER", "x-token-auth")

        return self.create_server_url(
            auth=f"{user}:{self.token}" if user else self.token,
            path=f"/{self.owner}/{self.repo_name}.git",
        )

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        """
        Get the Bitbucket comparison link between two version tags.
        :param from_rev: The older version to compare.
        :param to_rev: The newer version to compare.
        :return: Link to view a comparison between the two versions.
        """
        return self.create_repo_url(
            repo_path=f"/branches/compare/{from_rev}%0D{to_rev}"
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_repo_url(repo_path=f"/commits/{commit_hash}")

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
            return self.create_repo_url(repo_path=f"/pull-requests/{pr_number}")

        return ""

    @staticmethod
    def format_w_official_vcs_name(format_str: str) -> str:
        if "%s" in format_str:
            return format_str % Bitbucket.OFFICIAL_NAME

        if "{}" in format_str:
            return format_str.format(Bitbucket.OFFICIAL_NAME)

        if "{vcs_name}" in format_str:
            return format_str.format(vcs_name=Bitbucket.OFFICIAL_NAME)

        return format_str

    def get_changelog_context_filters(self) -> tuple[Callable[..., Any], ...]:
        return (
            self.create_server_url,
            self.create_repo_url,
            self.commit_hash_url,
            self.compare_url,
            self.pull_request_url,
            self.format_w_official_vcs_name,
        )

    def upload_dists(self, tag: str, dist_glob: str) -> int:
        return super().upload_dists(tag, dist_glob)

    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int | str:
        return super().create_or_update_release(tag, release_notes, prerelease)

    def create_release(
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,
        assets: list[str] | None = None,
        noop: bool = False,
    ) -> int | str:
        return super().create_release(tag, release_notes, prerelease, assets, noop)


RemoteHvcsBase.register(Bitbucket)
