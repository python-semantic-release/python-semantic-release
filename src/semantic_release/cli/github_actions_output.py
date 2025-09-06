from __future__ import annotations

import os
from enum import Enum
from re import compile as regexp
from typing import TYPE_CHECKING

from semantic_release.globals import logger
from semantic_release.version.version import Version

if TYPE_CHECKING:
    from typing import Any

    from semantic_release.hvcs.github import Github


class PersistenceMode(Enum):
    TEMPORARY = "temporary"
    PERMANENT = "permanent"


class VersionGitHubActionsOutput:
    OUTPUT_ENV_VAR = "GITHUB_OUTPUT"

    def __init__(
        self,
        gh_client: Github | None = None,
        mode: PersistenceMode = PersistenceMode.PERMANENT,
        released: bool | None = None,
        version: Version | None = None,
        commit_sha: str | None = None,
        release_notes: str | None = None,
        prev_version: Version | None = None,
    ) -> None:
        self._gh_client = gh_client
        self._mode = mode
        self._released = released
        self._version = version
        self._commit_sha = commit_sha
        self._release_notes = release_notes
        self._prev_version = prev_version

    @property
    def released(self) -> bool | None:
        return self._released

    @released.setter
    def released(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("output 'released' is boolean")
        self._released = value

    @property
    def version(self) -> Version | None:
        return self._version if self._version is not None else None

    @version.setter
    def version(self, value: Version) -> None:
        if not isinstance(value, Version):
            raise TypeError("output 'released' should be a Version")
        self._version = value

    @property
    def tag(self) -> str | None:
        return self.version.as_tag() if self.version is not None else None

    @property
    def is_prerelease(self) -> bool | None:
        return self.version.is_prerelease if self.version is not None else None

    @property
    def commit_sha(self) -> str | None:
        return self._commit_sha if self._commit_sha else None

    @commit_sha.setter
    def commit_sha(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("output 'commit_sha' should be a string")

        if not regexp(r"^[0-9a-f]{40}$").match(value):
            raise ValueError(
                "output 'commit_sha' should be a valid 40-hex-character SHA"
            )

        self._commit_sha = value

    @property
    def release_notes(self) -> str | None:
        return self._release_notes if self._release_notes else None

    @release_notes.setter
    def release_notes(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("output 'release_notes' should be a string")
        self._release_notes = value

    @property
    def prev_version(self) -> Version | None:
        if not self.released:
            return self.version
        return self._prev_version if self._prev_version else None

    @prev_version.setter
    def prev_version(self, value: Version) -> None:
        if not isinstance(value, Version):
            raise TypeError("output 'prev_version' should be a Version")
        self._prev_version = value

    @property
    def gh_client(self) -> Github:
        if not self._gh_client:
            raise ValueError("GitHub client not set, cannot create links")
        return self._gh_client

    def to_output_text(self) -> str:
        missing: set[str] = set()
        if self.version is None:
            missing.add("version")
        if self.released is None:
            missing.add("released")
        if self.released:
            if self.release_notes is None:
                missing.add("release_notes")
            if self._mode is PersistenceMode.PERMANENT and self.commit_sha is None:
                missing.add("commit_sha")

        if missing:
            raise ValueError(
                f"some required outputs were not set: {', '.join(missing)}"
            )

        output_values: dict[str, Any] = {
            "released": str(self.released).lower(),
            "version": str(self.version),
            "tag": self.tag,
            "is_prerelease": str(self.is_prerelease).lower(),
            "link": self.gh_client.create_release_url(self.tag) if self.tag else "",
            "previous_version": str(self.prev_version) if self.prev_version else "",
            "commit_sha": self.commit_sha if self.commit_sha else "",
        }

        multiline_output_values: dict[str, str] = {
            "release_notes": self.release_notes if self.release_notes else "",
        }

        output_lines = [
            *[f"{key}={value!s}{os.linesep}" for key, value in output_values.items()],
            *[
                f"{key}<<EOF{os.linesep}{value}EOF{os.linesep}"
                if value
                else f"{key}={os.linesep}"
                for key, value in multiline_output_values.items()
            ],
        ]

        return str.join("", output_lines)

    def write_if_possible(self, filename: str | None = None) -> None:
        output_file = filename or os.getenv(self.OUTPUT_ENV_VAR)
        if not output_file:
            logger.info("not writing GitHub Actions output, as no file specified")
            return

        with open(output_file, "ab") as f:
            f.write(self.to_output_text().encode("utf-8"))
