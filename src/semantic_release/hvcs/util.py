from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore[import]

from semantic_release.globals import logger

if TYPE_CHECKING:  # pragma: no cover
    from semantic_release.hvcs.token_auth import TokenAuth


def build_requests_session(
    raise_for_status: bool = True,
    retry: bool | int | Retry = True,
    auth: TokenAuth | None = None,
) -> Session:
    """
    Create a requests session.

    :param raise_for_status: If True, a hook to invoke raise_for_status be installed
    :param retry: If true, it will use default Retry configuration. if an integer, it
        will use default Retry configuration with given integer as total retry
        count. if Retry instance, it will use this instance.
    :param auth: Optional TokenAuth instance to be used to provide the Authorization
        header to the session

    :return: configured requests Session
    """
    session = Session()
    if raise_for_status:
        session.hooks = {"response": [lambda r, *_, **__: r.raise_for_status()]}

    if retry:
        if isinstance(retry, bool):
            retry = Retry()
        elif isinstance(retry, int):
            retry = Retry(retry)
        elif not isinstance(retry, Retry):
            raise ValueError("retry should be a bool, int or Retry instance.")
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    if auth:
        logger.debug("setting up default session authentication")
        session.auth = auth

    return session


_R = TypeVar("_R")


def suppress_http_error_for_codes(
    *codes: int,
) -> Callable[[Callable[..., _R]], Callable[..., _R | None]]:
    """
    For the codes given, return a decorator that will suppress HTTPErrors that are
    raised from responses that came with one of those status codes. The function will
    return False instead of raising the HTTPError
    """

    def _suppress_http_error_for_codes(
        func: Callable[..., _R],
    ) -> Callable[..., _R | None]:
        @wraps(func)
        def _wrapper(*a: Any, **kw: Any) -> _R | None:
            try:
                return func(*a, **kw)
            except HTTPError as err:
                if err.response and err.response.status_code in codes:
                    logger.warning(
                        "%s received response %s: %s",
                        func.__qualname__,
                        err.response.status_code,
                        str(err),
                    )
                return None

        return _wrapper

    return _suppress_http_error_for_codes


suppress_not_found = suppress_http_error_for_codes(404)
