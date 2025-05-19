"""Common functionality and interface for interacting with Git remote VCS"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from urllib3.util.url import Url, parse_url

from semantic_release.hvcs import HvcsBase

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class RemoteHvcsBase(HvcsBase, metaclass=ABCMeta):
    """
    Interface for subclasses interacting with a remote VCS

    This abstract class is defined to provide common helper functions and
    a set of basic methods that all remote VCS environments usually support.

    If the remote vcs implementation (via subclass) does not support a functionality
    then it can just call super()'s method which defaults as a non-supported log
    message and empty results.  This is more straightforward than checking for
    NotImplemented around every function call in the core library code.
    """

    DEFAULT_ENV_TOKEN_NAME = "HVCS_TOKEN"  # noqa: S105

    def __init__(self, remote_url: str, *_args: Any, **_kwargs: Any) -> None:
        super().__init__(remote_url)
        self._hvcs_domain: Url | None = None
        self._api_url: Url | None = None

    @property
    def hvcs_domain(self) -> Url:
        if self._hvcs_domain is None:
            raise RuntimeError("Property 'hvcs_domain' was used before it was set!")
        return self._hvcs_domain

    @property
    def api_url(self) -> Url:
        if self._api_url is None:
            raise RuntimeError("Property 'api_url' was used before it was set!")
        return self._api_url

    @abstractmethod
    def upload_dists(self, tag: str, dist_glob: str) -> int:
        """
        Upload built distributions to a release on a remote VCS that
        supports such uploads
        """
        self._not_supported(self.upload_dists.__name__)
        return 0

    @abstractmethod
    def create_release(
        self,
        tag: str,
        release_notes: str,
        prerelease: bool = False,
        assets: list[str] | None = None,
        noop: bool = False,
    ) -> int | str:
        """
        Create a release in a remote VCS, if supported

        Which includes uploading any assets as part of the release
        """
        self._not_supported(self.create_release.__name__)
        return -1

    @abstractmethod
    def create_or_update_release(
        self, tag: str, release_notes: str, prerelease: bool = False
    ) -> int | str:
        """
        Create or update a release for the given tag in a remote VCS, attaching the
        given changelog, if supported
        """
        self._not_supported(self.create_or_update_release.__name__)
        return -1

    def create_server_url(
        self,
        path: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        # Ensure any path prefix is transferred but not doubled up on the derived url
        normalized_path = (
            f"{self.hvcs_domain.path}/{path}"
            if self.hvcs_domain.path and not path.startswith(self.hvcs_domain.path)
            else path
        )
        return self._derive_url(
            self.hvcs_domain,
            path=normalized_path,
            auth=auth,
            query=query,
            fragment=fragment,
        )

    def create_repo_url(
        self,
        repo_path: str,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        return self.create_server_url(
            path=f"/{self.owner}/{self.repo_name}/{repo_path}",
            query=query,
            fragment=fragment,
        )

    def create_api_url(
        self,
        endpoint: str,
        auth: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
    ) -> str:
        # Ensure any api path prefix is transferred but not doubled up on the derived api url
        normalized_endpoint = (
            f"{self.api_url.path}/{endpoint}"
            if self.api_url.path and not endpoint.startswith(self.api_url.path)
            else endpoint
        )
        return self._derive_url(
            self.api_url,
            path=normalized_endpoint,
            auth=auth,
            query=query,
            fragment=fragment,
        )

    @staticmethod
    def _derive_url(
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
                    "path": str(PurePosixPath("/", path.lstrip("/"))),
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

    @staticmethod
    def _validate_url_scheme(url: Url, allow_insecure: bool = False) -> None:
        if url.scheme == "http" and not allow_insecure:
            raise ValueError("Insecure connections are currently disabled.")

        if url.scheme not in ["http", "https"]:
            raise ValueError(
                f"Invalid scheme {url.scheme} for {url.host}. "
                "Only http and https are supported."
            )

    @staticmethod
    def _normalize_url(url: Url | str, allow_insecure: bool = False) -> Url:
        """
        Function to ensure url scheme is populated & allowed

        Raises
        ------
        TypeError: when url parameter is not a string or parsable url
        ValueError: when the url scheme is not http or https

        """
        tgt_url = parse_url(url) if isinstance(url, str) else url
        if not isinstance(tgt_url, Url):
            raise TypeError(
                f"Invalid url type ({type(tgt_url)}) received, expected Url or string"
            )

        if not tgt_url.scheme:
            new_scheme = "http" if allow_insecure else "https"
            tgt_url = Url(**{**tgt_url._asdict(), "scheme": new_scheme})

        RemoteHvcsBase._validate_url_scheme(tgt_url, allow_insecure=allow_insecure)
        return tgt_url
