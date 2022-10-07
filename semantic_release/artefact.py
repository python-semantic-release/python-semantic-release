"""Helper for using Twine to upload to an artifact repository.
"""
import logging
import os
from dataclasses import InitVar
from dataclasses import asdict as dataclass_asdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from twine.commands.upload import upload as twine_upload
from twine.exceptions import TwineException
from twine.settings import Settings as TwineSettings

from semantic_release import ImproperConfigurationError
from semantic_release.helpers import LoggedFunction
from semantic_release.settings import config

logger = logging.getLogger(__name__)


def get_env_var(name: str) -> Optional[str]:
    """
    Resolve variable name from config and return matching environment variable

    :param name: Variable name to retrieve from environment

    :returns Value of environment variable or None if not set.
    """
    return os.environ.get(config.get(name))


@dataclass(eq=False)
class ArtifactRepo:
    """
    Object that manages the configuration and execution of upload using Twine.

    This object needs only one shared argument to be instantiated.
    """

    dist_path: InitVar[Path]
    repository_name: str = "pypi"
    repository_url: Optional[str] = None
    username: Optional[str] = field(repr=False, default=None)
    password: Optional[str] = field(repr=False, default=None)
    dists: List[str] = field(init=False, default_factory=list)

    def __post_init__(self, dist_path: Path) -> None:
        """
        :param dist_path: Path to dist folder containing the files to upload.
        """
        self._handle_credentials_init()
        self._handle_repository_config()
        self._handle_glob_patterns(dist_path)

    @LoggedFunction(logger)
    def _handle_credentials_init(self) -> None:
        """
        Initialize credentials from environment variables.

        For the transitional period until the *pypi* variables can be safely removed,
        additional complexity is needed.

        :raises ImproperConfigurationError:
            Error while setting up credentials configuration.
        """
        username = get_env_var("repository_user_var") or get_env_var("pypi_user_var")
        password = (
            get_env_var("repository_pass_var")
            or get_env_var("pypi_pass_var")
            or get_env_var("pypi_token_var")
        )
        if username and password:
            self.username = username
            self.password = password
        elif password and not username:
            self.username = username or "__token__"
            self.password = password
            logger.warning(
                "Providing only password or token without username is deprecated"
            )
        # neither username nor password provided, check for ~/.pypirc file
        elif not Path("~/.pypirc").expanduser().exists():
            raise ImproperConfigurationError(
                "Missing credentials for uploading to artifact repository"
            )

    @LoggedFunction(logger)
    def _handle_glob_patterns(self, dist_path: Path) -> None:
        """
        Load glob patterns that select the distribution files to publish.

        :param dist_path: Path to folder with package files
        """
        glob_patterns = config.get("dist_glob_patterns") or config.get(
            "upload_to_pypi_glob_patterns"
        )
        glob_patterns = (glob_patterns or "*").split(",")

        self.dists = [str(dist_path.joinpath(pattern)) for pattern in glob_patterns]

    @LoggedFunction(logger)
    def _handle_repository_config(self) -> None:
        """
        Initialize repository settings from config.

        *repository_url* overrides *repository*, Twine handles this the same way.

        Defaults to repository_name `pypi` when both are not set.
        """
        repository_url = get_env_var("repository_url_var") or config.get(
            "repository_url"
        )
        repository_name = config.get("repository")

        if repository_url:
            self.repository_url = repository_url
        elif repository_name:
            self.repository_name = repository_name

    @LoggedFunction(logger)
    def _create_twine_settings(self, addon_kwargs: Dict[str, Any]) -> TwineSettings:
        """
        Gather all parameters that had a value set during instantiation and
        pass them to Twine which then validates and loads the config.
        """
        params = {name: val for name, val in dataclass_asdict(self).items() if val}
        settings = TwineSettings(**params, **addon_kwargs)

        return settings

    @LoggedFunction(logger)
    def upload(
        self, noop: bool, verbose: bool, skip_existing: bool, **additional_kwargs
    ) -> bool:
        """
        Upload artifact to repository using Twine.

        For known repositories (like PyPI), the web URLs of successfully uploaded packages
        will be displayed.

        :param noop: Do not apply any changes..
        :param verbose: Show verbose output for Twine.
        :param skip_existing: Continue uploading files if one already exists.
            (May not work, check your repository for support.)

        :raises ImproperConfigurationError:
            The upload failed due to a configuration error.

        :returns True if successful, False otherwise.
        """
        addon_kwargs = {
            "non_interactive": True,
            "verbose": verbose,
            "skip_existing": skip_existing,
            **additional_kwargs,
        }

        try:
            twine_settings = self._create_twine_settings(addon_kwargs)
            if not noop:
                twine_upload(upload_settings=twine_settings, dists=self.dists)
        except TwineException as e:
            raise ImproperConfigurationError(
                "Upload to artifact repository has failed"
            ) from e
        except requests.HTTPError as e:
            logger.warning(f"Upload to artifact repository has failed: {e}")
            return False
        else:
            return True

    @staticmethod
    def upload_enabled() -> bool:
        """
        Check if artifact repository upload is enabled

        :returns True if upload is enabled, False otherwise.
        """
        return config.get("upload_to_repository") and config.get("upload_to_pypi")
