"""Helper code for interacting with a Bitbucket remote VCS"""

# Note: Bitbucket doesn't support releases. But it allows users to use
# `semantic-release version` without having to specify `--no-vcs-release`.

from __future__ import annotations

import logging
import mimetypes
import os
from functools import lru_cache

from urllib3.util.url import Url, parse_url

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


class Bitbucket(HvcsBase):
    """Bitbucket helper class"""

    DEFAULT_DOMAIN = "bitbucket.org"
    DEFAULT_API_SUBDOMAIN_PREFIX = "api"
    DEFAULT_API_DOMAIN = f"{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}"
    DEFAULT_API_PATH_CLOUD = "/2.0"
    DEFAULT_API_PATH_ONPREM = "/rest/api/1.0"
    DEFAULT_ENV_TOKEN_NAME = "BITBUCKET_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
    ) -> None:
        self._remote_url = remote_url

        domain_url = parse_url(hvcs_domain or self.DEFAULT_DOMAIN)

        # Strip any scheme, query or fragment from the domain
        self.hvcs_domain = Url(
            host=domain_url.host, port=domain_url.port, path=domain_url.path
        ).url.rstrip("/")

        if self.hvcs_domain == self.DEFAULT_DOMAIN:
            # BitBucket Cloud detected, which means it uses a separate api domain
            self.hvcs_api_domain = self.DEFAULT_API_DOMAIN

            # ref: https://developer.atlassian.com/cloud/bitbucket/rest/intro/#uri-uuid
            self.api_url = Url(
                scheme="https",
                host=self.hvcs_api_domain,
                path=self.DEFAULT_API_PATH_CLOUD,
            ).url.rstrip("/")

        else:
            # BitBucket Server (on premise) detected, which uses a path prefix for the api
            # ref: https://developer.atlassian.com/server/bitbucket/how-tos/command-line-rest/
            api_domain_parts = parse_url(
                hvcs_api_domain
                or Url(
                    # infer from Domain url and append the api path
                    scheme=domain_url.scheme,
                    host=self.hvcs_domain,
                    path=self.DEFAULT_API_PATH_ONPREM,
                ).url
            )

            # Strip any scheme, query or fragment from the api domain
            self.hvcs_api_domain = Url(
                host=api_domain_parts.host,
                port=api_domain_parts.port,
                path=str.replace(
                    api_domain_parts.path or "", self.DEFAULT_API_PATH_ONPREM, ""
                ),
            ).url.rstrip("/")

            self.api_url = Url(
                scheme=api_domain_parts.scheme or "https",
                host=self.hvcs_api_domain,
                path=self.DEFAULT_API_PATH_ONPREM,
            ).url.rstrip("/")

        self.token = token
        auth = None if not self.token else TokenAuth(self.token)
        self.session = build_requests_session(auth=auth)

    @lru_cache(maxsize=1)
    def _get_repository_owner_and_name(self) -> tuple[str, str]:
        # ref: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        if "BITBUCKET_REPO_FULL_NAME" in os.environ:
            log.info("Getting repository owner and name from environment variables.")
            owner, name = os.environ["BITBUCKET_REPO_FULL_NAME"].rsplit("/", 1)
            return owner, name
        return super()._get_repository_owner_and_name()

    def compare_url(self, from_rev: str, to_rev: str) -> str:
        """
        Get the Bitbucket comparison link between two version tags.
        :param from_rev: The older version to compare.
        :param to_rev: The newer version to compare.
        :return: Link to view a comparison between the two versions.
        """
        return (
            f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/"
            f"branches/compare/{from_rev}%0D{to_rev}"
        )

    def remote_url(self, use_token: bool = True) -> str:
        if not use_token:
            # Note: Assume the user is using SSH.
            return self._remote_url
        if not self.token:
            raise ValueError("Requested to use token but no token set.")
        user = os.environ.get("BITBUCKET_USER")
        if user:
            # Note: If the user is set, assume the token is an app secret. This will work
            # on any repository the user has access to.
            # https://support.atlassian.com/bitbucket-cloud/docs/push-back-to-your-repository
            return (
                f"https://{user}:{self.token}@"
                f"{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
            )
        # Note: Assume the token is a repository token which will only work on the
        # repository it was created for.
        # https://support.atlassian.com/bitbucket-cloud/docs/using-access-tokens
        return (
            f"https://x-token-auth:{self.token}@"
            f"{self.hvcs_domain}/{self.owner}/{self.repo_name}.git"
        )

    def commit_hash_url(self, commit_hash: str) -> str:
        return (
            f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/"
            f"commits/{commit_hash}"
        )

    def pull_request_url(self, pr_number: str | int) -> str:
        return (
            f"https://{self.hvcs_domain}/{self.owner}/{self.repo_name}/"
            f"pull-requests/{pr_number}"
        )
