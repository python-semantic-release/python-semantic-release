import importlib
import logging
import re
import string
from functools import lru_cache, wraps
from pathlib import PurePosixPath
from typing import Any, Callable, NamedTuple, TypeVar
from urllib.parse import urlsplit

log = logging.getLogger(__name__)


def format_arg(value: Any) -> str:
    """Helper to format an argument an argument for logging"""
    if type(value) == str:
        return f"'{value.strip()}'"
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
    Decorator which adds debug logging of a function's input arguments and return
    value.

    The input arguments are logged before the function is called, and the
    return value is logged once it has completed.

    :param logger: Logger to send output to.
    """

    def _logged_function(func: _FuncType[_R]) -> _FuncType[_R]:
        @wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> _R:
            logger.debug(
                "%s(%s, %s)",
                func.__name__,
                ", ".join([format_arg(x) for x in args]),
                ", ".join([f"{k}={format_arg(v)}" for k, v in kwargs.items()]),
            )

            # Call function
            result = func(*args, **kwargs)

            # Log result
            logger.debug("%s -> %s", func.__qualname__, str(result))
            return result

        return _wrapper

    return _logged_function


@logged_function(log)
def dynamic_import(import_path: str) -> Any:
    """
    Dynamically import an object from a conventionally formatted "module:attribute"
    string
    """
    log.debug("Trying to import %s", import_path)
    module_name, attr = import_path.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


class ParsedGitUrl(NamedTuple):
    """Container for the elements parsed from a git URL"""

    scheme: str
    netloc: str
    namespace: str
    repo_name: str


@lru_cache(maxsize=512)
def parse_git_url(url: str) -> ParsedGitUrl:
    """
    Attempt to parse a string as a git url http[s]://, git://, file://, or ssh format, into a
    ParsedGitUrl.

    supported examples:
        http://git.mycompany.com/username/myproject.git
        https://github.com/username/myproject.git
        https://gitlab.com/group/subgroup/myproject.git
        https://git.mycompany.com:4443/username/myproject.git
        git://host.xz/path/to/repo.git/
        git://host.xz:9418/path/to/repo.git/
        git@github.com:username/myproject.git                  <-- assumes ssh://
        ssh://git@github.com:3759/myproject.git                <-- non-standard, but assume user 3759
        ssh://git@github.com:username/myproject.git
        ssh://git@bitbucket.org:7999/username/myproject.git
        git+ssh://git@github.com:username/myproject.git
        /Users/username/dev/remote/myproject.git               <-- Posix File paths
        file:///Users/username/dev/remote/myproject.git
        C:/Users/username/dev/remote/myproject.git             <-- Windows File paths
        file:///C:/Users/username/dev/remote/myproject.git

    REFERENCE: https://stackoverflow.com/questions/31801271/what-are-the-supported-git-url-formats

    Raises ValueError if the url can't be parsed.
    """
    log.debug("Parsing git url %r", url)

    # Normalizers are a list of tuples of (pattern, replacement)
    normalizers = [
        # normalize implicit ssh urls to explicit ssh://
        (r"^([\w._-]+@)", r"ssh://\1"),
        # normalize git+ssh:// urls to ssh://
        (r"^git\+ssh://", "ssh://"),
        # normalize an scp like syntax to URL compatible syntax
        # excluding port definitions (:#####) & including numeric usernames
        (r"(ssh://(?:[\w._-]+@)?[\w.-]+):(?!\d{1,5}/\w+/)(.*)$", r"\1/\2"),
        # normalize implicit file (windows || posix) urls to explicit file:// urls
        (r"^([C-Z]:/)|^/(\w)", r"file:///\1\2"),
    ]

    for pattern, replacement in normalizers:
        url = re.compile(pattern).sub(replacement, url)

    # run the url through urlsplit to separate out the parts
    urllib_split = urlsplit(url)

    # Fail if url scheme not found
    if not urllib_split.scheme:
        raise ValueError(f"Cannot parse {url!r}")

    # We have been able to parse the url with urlsplit,
    # so it's a (file|git|ssh|https?)://... structure
    # but we aren't validating the protocol scheme as its not our business

    # use PosixPath to normalize the path & then separate out the namespace & repo_name
    namespace, _, name = (
        str(PurePosixPath(urllib_split.path)).lstrip("/").rpartition("/")
    )

    # strip out the .git at the end of the repo_name if present
    name = name[:-4] if name.endswith(".git") else name

    # check that we have all the required parts of the url
    required_parts = [
        urllib_split.scheme,
        # Allow empty net location for file:// urls
        True if urllib_split.scheme == "file" else urllib_split.netloc,
        namespace,
        name,
    ]

    if not all(required_parts):
        raise ValueError(f"Bad url: {url!r}")

    return ParsedGitUrl(
        scheme=urllib_split.scheme,
        netloc=urllib_split.netloc,
        namespace=namespace,
        repo_name=name,
    )
