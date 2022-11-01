import logging
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from requests import HTTPError, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from semantic_release.hvcs.token_auth import TokenAuth

logger = logging.getLogger(__name__)


def build_requests_session(
    raise_for_status=True,
    retry: Union[bool, int, Retry] = True,
    auth: Optional[TokenAuth] = None,
) -> Session:
    """
    Create a requests session.
    :param raise_for_status: If True, a hook to invoke raise_for_status be installed
    :param retry: If true, it will use default Retry configuration. if an integer, it will use default Retry
    configuration with given integer as total retry count. if Retry instance, it will use this instance.
    :return: configured requests Session
    """
    session = Session()
    if raise_for_status:
        session.hooks = {"response": [lambda r, *args, **kwargs: r.raise_for_status()]}

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
        session.auth = auth

    return session


def suppress_http_error(func: Callable[..., bool]) -> Callable[..., bool]:
    @wraps(func)
    def _wrapper(*a: Any, **kw: Any) -> bool:
        try:
            return func(*a, **kw)
        except HTTPError as err:
            logger.warning("%s failed: %s", func.__qualname__, err)
            return False

    return _wrapper


_R = TypeVar("_R")


def suppress_http_error_for_codes(
    *codes: int,
) -> Callable[[Callable[..., _R]], Callable[..., Optional[_R]]]:
    def suppress_http_error_for_codes(
        func: Callable[..., _R]
    ) -> Callable[..., Optional[_R]]:
        @wraps(func)
        def _wrapper(*a: Any, **kw: Any) -> Optional[_R]:
            try:
                return func(*a, **kw)
            except HTTPError as err:
                if err.response.status_code in codes:
                    logger.warning(
                        "%s received response %s: %s",
                        func.__qualname__,
                        err.response.status_code,
                        str(err),
                    )
                return None

        return _wrapper

    return suppress_http_error_for_codes


suppress_not_found = suppress_http_error_for_codes(404)
