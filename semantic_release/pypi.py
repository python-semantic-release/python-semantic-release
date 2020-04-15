"""Helper for using Twine to upload to PyPI.
"""
import logging

from invoke import run

from semantic_release import ImproperConfigurationError

from .helpers import LoggedFunction

logger = logging.getLogger(__name__)


@LoggedFunction(logger)
def upload_to_pypi(
    path: str = "dist",
    username: str = None,
    password: str = None,
    skip_existing: bool = False,
):
    """Upload wheels to PyPI with Twine.

    Wheels must already be created and stored at the given path.

    :param path: Path to dist folder containing the files to upload.
    :param username: PyPI account username.
    :param password: PyPI account password.
    :param skip_existing: Continue uploading files if one already exists.
        (Only valid when uploading to PyPI. Other implementations may not support this.)
    """
    if username is None or password is None or username == "" or password == "":
        raise ImproperConfigurationError("Missing credentials for uploading")

    run(
        "twine upload -u '{}' -p '{}' {} \"{}/*\"".format(
            username, password, "--skip-existing" if skip_existing else "", path
        )
    )
