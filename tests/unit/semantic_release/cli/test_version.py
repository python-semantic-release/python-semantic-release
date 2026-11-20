from pathlib import Path

import pytest
from git import Repo

from semantic_release.cli.commands.version import (
    is_forced_prerelease,
    version_from_forced_level,
)
from semantic_release.enums import LevelBump
from semantic_release.version.translator import VersionTranslator


@pytest.mark.parametrize(
    "force_prerelease, force_level, prerelease, expected",
    [
        *[
            (True, force_level, prerelease, True)
            for force_level in (None, "major", "minor", "patch")
            for prerelease in (True, False)
        ],
        *[
            (False, force_level, prerelease, False)
            for force_level in ("major", "minor", "patch")
            for prerelease in (True, False)
        ],
        *[(False, None, prerelease, prerelease) for prerelease in (True, False)],
    ],
)
def test_is_forced_prerelease(force_prerelease, force_level, prerelease, expected):
    assert is_forced_prerelease(force_prerelease, force_level, prerelease) == expected


def test_version_from_forced_level_only_considers_head_history(tmp_path: Path):
    # A higher tag exists on a side branch that is NOT in HEAD's history.
    # A forced bump must be based on the history reachable from HEAD (hotfix),
    # not on the highest tag in the whole repository.
    repo = Repo.init(tmp_path)
    try:
        base = repo.index.commit("base")
        repo.create_tag("v1.2.0", ref=base)

        side = repo.index.commit("side work", parent_commits=(base,), head=False)
        repo.create_tag("v1.4.0", ref=side)

        hotfix = repo.index.commit("fix: hotfix", parent_commits=(base,))
        repo.create_tag("v1.2.1", ref=hotfix)

        result = version_from_forced_level(
            repo_dir=Path(repo.working_dir),
            forced_level_bump=LevelBump.PATCH,
            translator=VersionTranslator(),
        )
    finally:
        repo.close()

    assert str(result) == "1.2.2"
