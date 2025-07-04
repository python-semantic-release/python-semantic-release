from __future__ import annotations

import os
from re import compile as regexp

from semantic_release.globals import logger
from semantic_release.version.version import Version


class VersionGitHubActionsOutput:
    OUTPUT_ENV_VAR = "GITHUB_OUTPUT"

    def __init__(
        self,
        released: bool | None = None,
        version: Version | None = None,
        commit_sha: str | None = None,
    ) -> None:
        self._released = released
        self._version = version
        self._commit_sha = commit_sha

    @property
    def released(self) -> bool | None:
        return self._released

    @released.setter
    def released(self, value: bool) -> None:
        if type(value) is not bool:
            raise TypeError("output 'released' is boolean")
        self._released = value

    @property
    def version(self) -> Version | None:
        return self._version if self._version is not None else None

    @version.setter
    def version(self, value: Version) -> None:
        if type(value) is not Version:
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

    def to_output_text(self) -> str:
        missing = set()
        if self.version is None:
            missing.add("version")
        if self.released is None:
            missing.add("released")
        if self.released and self.commit_sha is None:
            missing.add("commit_sha")

        if missing:
            raise ValueError(
                f"some required outputs were not set: {', '.join(missing)}"
            )

        outputs = {
            "released": str(self.released).lower(),
            "version": str(self.version),
            "tag": self.tag,
            "is_prerelease": str(self.is_prerelease).lower(),
            "commit_sha": self.commit_sha if self.commit_sha else "",
        }

        return str.join("", [f"{key}={value!s}\n" for key, value in outputs.items()])

    def write_if_possible(self, filename: str | None = None) -> None:
        output_file = filename or os.getenv(self.OUTPUT_ENV_VAR)
        if not output_file:
            logger.info("not writing GitHub Actions output, as no file specified")
            return

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(self.to_output_text())
