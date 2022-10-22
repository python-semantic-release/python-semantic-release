import importlib
import logging
import re
import string
from functools import wraps
from typing import Any, Callable, NamedTuple, TypeVar
from urllib.parse import urlsplit


def format_arg(value: Any) -> str:
    if type(value) == str:
        return f"'{value.strip()}'"
    else:
        return str(value)


def check_tag_format(tag_format: str) -> None:
    if "version" not in (f[1] for f in string.Formatter().parse(tag_format)):
        raise ValueError(
            f"Invalid tag_format {tag_format!r}, must use 'version' as a format key"
        )


_R = TypeVar("_R")
_FuncType = Callable[..., _R]


def logged_function(logger: logging.Logger) -> Callable[[_FuncType[_R]], _FuncType[_R]]:
    """
    Decorator which adds debug logging to a function.

    The input arguments are logged before the function is called, and the
    return value is logged once it has completed.

    :param logger: Logger to send output to.
    """

    def _logged_function(func: _FuncType[_R]) -> _FuncType[_R]:
        @wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> _R:
            # Log function name and arguments
            logger.debug(
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
                logger.debug(f"{func.__name__} -> {result}")
            return result

        return _wrapper

    return _logged_function


LoggedFunction = logged_function


def dynamic_import(import_path: str) -> Any:
    module_name, _, attr = import_path.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


class ParsedGitUrl(NamedTuple):
    scheme: str
    netloc: str
    namespace: str
    repo_name: str


GIT_URL_REGEX = re.compile(
    r"""
    ^
    git@
    (?P<netloc>[^:]+)
    :
    (?P<namespace>[\w\.@\:/\-~]+)
    /
    (?P<repo_name>[\w\.\_\-]+)  # Note this also catches the ".git" at the end if present
    /?
    $
    """,
    flags=re.VERBOSE,
)


def parse_git_url(url: str) -> ParsedGitUrl:
    urllib_split = urlsplit(url)
    if urllib_split.scheme:
        # We have been able to parse the url with urlsplit,
        # so it's a (git|ssh|https?)://... structure
        namespace, _, name = urllib_split.path.lstrip("/").rpartition("/")
        name.rstrip("/")
        name = name[:-4] if name.endswith(".git") else name
        if not all((urllib_split.scheme, urllib_split.netloc, namespace, name)):
            raise ValueError(f"Bad url: {url!r}")

        return ParsedGitUrl(
            scheme=urllib_split.scheme,
            netloc=urllib_split.netloc,
            namespace=namespace,
            repo_name=name,
        )

    m = GIT_URL_REGEX.match(url)
    if not m:
        raise ValueError(f"Cannot parse {url!r}")

    repo_name = m.group("repo_name")
    repo_name = repo_name[:-4] if repo_name.endswith(".git") else repo_name

    if not all((*m.group("netloc", "namespace"), repo_name)):
        raise ValueError(f"Bad url: {url!r}")
    return ParsedGitUrl(
        scheme="git",
        netloc=m.group("netloc"),
        namespace=m.group("namespace"),
        repo_name=repo_name,
    )
