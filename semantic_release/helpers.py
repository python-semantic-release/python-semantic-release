import functools
from typing import Union

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def format_arg(value):
    if type(value) == str:
        return f"'{value.strip()}'"
    else:
        return str(value)


def build_requests_session(
    raise_for_status=True, retry: Union[bool, int, Retry] = True
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
    return session


class LoggedFunction:
    """
    Decorator which adds debug logging to a function.

    The input arguments are logged before the function is called, and the
    return value is logged once it has completed.

    :param logger: Logger to send output to.
    """

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        @functools.wraps(func)
        def logged_func(*args, **kwargs):
            # Log function name and arguments
            self.logger.debug(
                "{function}({args}{kwargs})".format(
                    function=func.__name__,
                    args=", ".join([format_arg(x) for x in args]),
                    kwargs="".join(
                        [f", {k}={format_arg(v)}" for k, v in kwargs.items()]
                    ),
                )
            )

            # Call function
            result = func(*args, **kwargs)

            # Log result
            if result is not None:
                self.logger.debug(f"{func.__name__} -> {result}")
            return result

        return logged_func
