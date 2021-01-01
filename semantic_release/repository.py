"""Helper for using Twine to upload to an artifact repository.
"""
import logging
import os
from typing import List

from invoke import run

from semantic_release import ImproperConfigurationError

from semantic_release.settings import config

from .helpers import LoggedFunction

logger = logging.getLogger(__name__)


class Repository(object):

    def __init__(self, username: str = None, password: str = None) -> None:
        self._username = username if username else os.environ.get("REPOSITORY_USERNAME")
        self._password = password if password else os.environ.get("REPOSITORY_PASSWORD")
        if not self._username or not self._password:
            raise ImproperConfigurationError("Missing credentials for uploading to repository")
        self.repository_url = config.get('repository_url', None)
        super().__init__()


    @LoggedFunction(logger)
    def upload(self, path: str = "dist", skip_existing: bool = False, glob_patterns: List[str] = None):
        """
        Upload artifact to repository with twine

        :param path: Path to dist folder containing the files to upload.
        :param skip_existing: Continue uploading files if one already exists.
            (Only valid when uploading to PyPI. Other implementations may not support this.)
        :param glob_patterns: List of glob patterns to include in the upload (["*"] by default)."""
        if not glob_patterns:
            glob_patterns = ["*"]
        dist = " ".join(
            ['"{}/{}"'.format(path, glob_pattern.strip()) for glob_pattern in glob_patterns]
        )

        extra_parms = " ".join([""] + self._extra_twine_arguments()) if self._extra_twine_arguments() else ""
        extra_parms += " --skip-existing" if skip_existing else ""

        run(f"twine upload -u '{self._username}' -p '{self._password}'{extra_parms} {dist}")

    def _extra_twine_arguments(self) -> List[str]:
        return [f"--repository-url '{self.repository_url}'"] if self.repository_url else []


def get_repository() -> Repository:
    """Return an artifact repository preconfigured based on env variables
    """
    token = os.environ.get("PYPI_TOKEN")
    if not token:
        return Repository(os.environ.get("PYPI_USERNAME"), os.environ.get("PYPI_PASSWORD"))
    elif token.startswith("pypi-"):
        return Repository("__token__", token)
    else:
        raise ImproperConfigurationError('PyPI token should begin with "pypi-"')
