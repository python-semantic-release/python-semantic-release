import pytest

from semantic_release.cli.commands.version import is_forced_prerelease


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
