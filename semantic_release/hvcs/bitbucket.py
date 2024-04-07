"""Helper code for interacting with a Bitbucket remote VCS"""

# Note: Bitbucket doesn't support releases. But it allows users to use
# `semantic-release version` without having to specify `--no-vcs-release`.

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import PurePosixPath

from urllib3.util.url import Url, parse_url

from semantic_release.hvcs._base import HvcsBase

log = logging.getLogger(__name__)


class Bitbucket(HvcsBase):
    """
    Bitbucket HVCS interface for interacting with BitBucket repositories

    This class supports the following products:
        - BitBucket Cloud
        - BitBucket Data Center Server (on-premises installations)
    """

    DEFAULT_DOMAIN = "bitbucket.org"
    DEFAULT_API_SUBDOMAIN_PREFIX = "api"
    DEFAULT_API_DOMAIN = f"{DEFAULT_API_SUBDOMAIN_PREFIX}.{DEFAULT_DOMAIN}"
    DEFAULT_API_PATH_CLOUD = "/2.0"
    DEFAULT_API_PATH_ONPREM = "/rest/api/1.0"
    DEFAULT_ENV_TOKEN_NAME = "BITBUCKET_TOKEN"  # noqa: S105

    def __init__(
        self,
        remote_url: str,
        *,
        hvcs_domain: str | None = None,
        hvcs_api_domain: str | None = None,
        token: str | None = None,
        allow_insecure: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(remote_url)
        self.token = token
        # NOTE: Uncomment in the future when we actually have functionalty to
        #       use the api, but currently there is none.
        # auth = None if not self.token else TokenAuth(self.token)
        # self.session = build_requests_session(auth=auth)

        domain_url = parse_url(hvcs_domain or f"https://{self.DEFAULT_DOMAIN}")

        if domain_url.scheme == "http" and not allow_insecure:
            raise ValueError("Insecure connections are currently disabled.")

        if not domain_url.scheme:
            new_scheme = "http" if allow_insecure else "https"
            domain_url = Url(
                **{
                    **domain_url._asdict(),
                    "scheme": new_scheme
                }
            )

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

        # Parse api domain if provided otherwise infer from domain
        api_domain_parts = parse_url(
            hvcs_api_domain
            or Url(
                # infer from Domain url and append the api path
                **{
                    **self.hvcs_domain._asdict(),
                    'host': self.hvcs_domain.host,
                    'path': str(
                        PurePosixPath(
                            str.lstrip(self.hvcs_domain.path or "", "/") or "/",
                            self.DEFAULT_API_PATH_ONPREM.lstrip("/"),
                        )
                    ),
                }
            ).url.rstrip("/")
        )

        if api_domain_parts.scheme == "http" and not allow_insecure:
            raise ValueError("Insecure connections are currently disabled.")

        if not api_domain_parts.scheme:
            new_scheme = "http" if allow_insecure else "https"
            api_domain_parts = Url(
                **{
                    **api_domain_parts._asdict(),
                    "scheme": new_scheme
                }
            )

        if api_domain_parts.scheme not in ["http", "https"]:
            raise ValueError(
                f"Invalid scheme {api_domain_parts.scheme} for api domain {api_domain_parts.host}. "
                "Only http and https are supported."
            )

        # As Bitbucket Cloud and Bitbucket Server (on-prem) have different api paths
        # lets check what we have been given and set the api url accordingly
        #   ref: https://developer.atlassian.com/server/bitbucket/how-tos/command-line-rest/
        #   NOTE: BitBucket Server (on premise) uses a path prefix '/rest/api/1.0' for the api
        #         while BitBucket Cloud uses a separate subdomain with '/2.0' path prefix
        is_bitbucket_cloud = bool(
            self.hvcs_domain.url == f"https://{self.DEFAULT_DOMAIN}"
        )

        # Calculate out the api url that we expect for Bitbucket Cloud
        default_cloud_api_url = parse_url(
            Url(
                # set api domain and append the default api path
                **{
                    **self.hvcs_domain._asdict(),
                    'host': f"{self.DEFAULT_API_DOMAIN}",
                    'path': self.DEFAULT_API_PATH_CLOUD,
                }
            ).url
        )

        if (
            is_bitbucket_cloud and hvcs_api_domain
            and api_domain_parts.url not in default_cloud_api_url.url
        ):
            # Api was provied but is not a subset of the expected one, raise an error
            # we check for a subset because the user may not have provided the full api path
            # but the correct domain.  If they didn't, then we are erroring out here.
            raise ValueError(
                f"Invalid api domain {api_domain_parts.url} for BitBucket Cloud. "
                f"Expected {default_cloud_api_url.url}."
            )

        # Set the api url to the default cloud one if we are on cloud, otherwise
        # use the verified api domain for a on-prem server
        self.api_url = default_cloud_api_url if is_bitbucket_cloud else parse_url(
            # Strip any auth, query or fragment from the domain
            Url(
                scheme=api_domain_parts.scheme,
                host=api_domain_parts.host,
                port=api_domain_parts.port,
                path=str(
                    PurePosixPath(
                        # pass any custom server prefix path but ensure we don't
                        # double up the api path in the case the user provided it
                        str.replace(
                            api_domain_parts.path or "", self.DEFAULT_API_PATH_ONPREM, ""
                        ).lstrip("/") or "/",
                        # apply the on-prem api path
                        self.DEFAULT_API_PATH_ONPREM.lstrip("/"),
                    )
                ),
            ).url.rstrip("/")
        )


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
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/branches/compare/{from_rev}%0D{to_rev}"
        )


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


    def commit_hash_url(self, commit_hash: str) -> str:
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/commits/{commit_hash}"
        )


    def pull_request_url(self, pr_number: str | int) -> str:
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/pull-requests/{pr_number}"
        )


    def _derive_url(self, base_url: Url, path: str, auth: str | None = None, query: str | None = None, fragment: str | None = None) -> str:
        overrides = dict(
            filter(
                lambda x: x[1] is not None,
                {
                    'auth': auth,
                    'path': str(PurePosixPath("/", path)),
                    'query': query,
                    'fragment': fragment,
                }.items()
            )
        )
        return Url(
            **{
                **base_url._asdict(),
                **overrides,
            }
        ).url.rstrip("/")


    def create_server_url(self, path: str, auth: str | None = None, query: str | None = None, fragment: str | None = None) -> str:
        return self._derive_url(self.hvcs_domain, path, auth, query, fragment)


    def create_api_url(self, endpoint: str, auth: str | None = None, query: str | None = None, fragment: str | None = None) -> str:
        return self._derive_url(self.api_url, endpoint, auth, query, fragment)
