import pytest

from semantic_release.history import version_history
from semantic_release.version import VersionTranslator, Version


@pytest.fixture
def a_repo_with_certain_tags():
    # TODO: This is a hacky fixture for sanity testing now,
    # and should be covered more thoroughly with a fixture with a
    # full repo of history by testing improvements
    class Tag:
        def __init__(self, name):
            self.name = name

    class Repo:
        def __init__(self):
            self.tags = [
                Tag("v0.1.0"),
                Tag("v1.0.1"),
                Tag("v0.2.0"),
                Tag("v2.1.0"),
                Tag("v0.3.0-dev.1"),
                Tag("v1.0.0"),
                Tag("v0.3.0"),
                Tag("v2.0.0-alpha.1"),
                Tag("v2.0.0-rc.1"),
                Tag("v1.0.4"),
                Tag("v2.0.0"),
            ]

    yield Repo()


def test_version_history(a_repo_with_certain_tags):
    translator = VersionTranslator()
    versions = version_history(a_repo_with_certain_tags, translator)

    assert versions == [
        Version.parse(v)
        for v in (
            "2.1.0",
            "2.0.0",
            "2.0.0-rc.1",
            "2.0.0-alpha.1",
            "1.0.4",
            "1.0.1",
            "1.0.0",
            "0.3.0",
            "0.3.0-dev.1",
            "0.2.0",
            "0.1.0",
        )
    ]


def test_next_version_correct(): pass
