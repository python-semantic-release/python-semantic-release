"""Helper for using Twine to upload to PyPI.
"""
import logging
import os
from typing import List

from invoke import run

from semantic_release import ImproperConfigurationError
from semantic_release.settings import config

from .helpers import LoggedFunction

logger = logging.getLogger(__name__)


@LoggedFunction(logger)
def upload_to_pypi(
    path: str = "dist", skip_existing: bool = False, glob_patterns: List[str] = None
):
    """Upload wheels to PyPI with Twine.

    Wheels must already be created and stored at the given path.

    Credentials are taken from either the environment variable
    ``PYPI_TOKEN``, or from ``PYPI_USERNAME`` and ``PYPI_PASSWORD``.

    :param path: Path to dist folder containing the files to upload.
    :param skip_existing: Continue uploading files if one already exists.
        (Only valid when uploading to PyPI. Other implementations may not support this.)
    :param glob_patterns: List of glob patterns to include in the upload (["*"] by default).
    """
    if not glob_patterns:
        glob_patterns = ["*"]

    # Attempt to get an API token from environment
    token = os.environ.get("PYPI_TOKEN")
    username = None
    password = None
    if not token:
        # Look for a username and password instead
        username = os.environ.get("PYPI_USERNAME")
        password = os.environ.get("PYPI_PASSWORD")
        home_dir = os.environ.get("HOME", "")
        if not (username or password) and (
            not home_dir or not os.path.isfile(os.path.join(home_dir, ".pypirc"))
        ):
            raise ImproperConfigurationError(
                "Missing credentials for uploading to PyPI"
            )
    elif not token.startswith("pypi-"):
        raise ImproperConfigurationError('PyPI token should begin with "pypi-"')
    else:
        username = "__token__"
        password = token

    repository = config.get("repository", None)
    repository_arg = f" -r '{repository}'" if repository else ""

    username_password = (
        f"-u '{username}' -p '{password}'" if username and password else ""
    )

    dist = " ".join(
        ['"{}/{}"'.format(path, glob_pattern.strip()) for glob_pattern in glob_patterns]
    )

    skip_existing_param = " --skip-existing" if skip_existing else ""

    run(f"twine upload {username_password}{repository_arg}{skip_existing_param} {dist}")
