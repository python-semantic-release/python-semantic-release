"""
NOTE: This is just an idea for now, it will change based on the implementation
"""
import pytest

from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version
from semantic_release.version.algorithm import get_next_version
from tests.const import (
    ANGULAR_COMMITS_PATCH,
    ANGULAR_COMMITS_MINOR,
    ANGULAR_COMMITS_MAJOR,
)
from tests.helper import add_text_to_file


@pytest.mark.parametrize(
    "commit_messages, translator, expected_new_version",
    [
        (ANGULAR_COMMITS_PATCH, VersionTranslator(), Version.parse("0.1.2")),
        (ANGULAR_COMMITS_MINOR, VersionTranslator(), Version.parse("0.2.0")),
        (ANGULAR_COMMITS_MAJOR, VersionTranslator(), Version.parse("1.0.0")),
    ],
)
@pytest.mark.parametrize(
    "repo_fixture_name",
    [
        "repo_with_single_branch",
        "repo_with_single_branch_and_prereleases",
        "repo_with_main_branch_and_feature_branches",
        "repo_with_git_flow",
        "repo_with_git_flow_and_release_channels",
    ],
)
@pytest.mark.parametrize("prerelease", (True, False))
def test_algorithm_angular_parser(
    request,
    repo_fixture_name,
    file_in_repo,
    commit_messages,
    translator,
    prerelease,
    expected_new_version,
):
    repo = request.getfixturevalue(repo_fixture_name)
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = get_next_version(repo, translator, prerelease)

    assert new_version == expected_new_version
