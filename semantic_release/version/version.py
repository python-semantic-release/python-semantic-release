from __future__ import annotations
import semver

from semantic_release.enums import LevelBump


class Version(semver.VersionInfo):
    def bump(self, level: LevelBump) -> Version:
        if level is LevelBump.MAJOR:
            return self.bump_major()
        if level is LevelBump.MINOR:
            return self.bump_minor()
        if level is LevelBump.PATCH:
            return self.bump_patch()
        return self
