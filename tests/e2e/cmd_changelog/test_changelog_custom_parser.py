from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.changelog.context import ChangelogMode

from tests.const import CHANGELOG_SUBCMD, MAIN_PROG_NAME
from tests.fixtures.repos import repo_w_no_tags_conventional_commits
from tests.util import (
    CustomConventionalParserWithIgnorePatterns,
    assert_successful_exit_code,
)

if TYPE_CHECKING:
    from pathlib import Path

    from semantic_release.commit_parser.conventional.parser import (
        ConventionalCommitParser,
    )

    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import UpdatePyprojectTomlFn, UseCustomParserFn
    from tests.fixtures.git_repo import BuiltRepoResult, GetCommitDefFn


@pytest.mark.parametrize(
    "repo_result", [lazy_fixture(repo_w_no_tags_conventional_commits.__name__)]
)
def test_changelog_custom_parser_remove_from_changelog(
    repo_result: BuiltRepoResult,
    run_cli: RunCliFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    use_custom_parser: UseCustomParserFn,
    get_commit_def_of_conventional_commit: GetCommitDefFn[ConventionalCommitParser],
    changelog_md_file: Path,
    default_md_changelog_insertion_flag: str,
    default_conventional_parser: ConventionalCommitParser,
):
    """
    Given when a changelog filtering custom parser is configured
    When provided a commit message that matches the ignore syntax
    Then the commit message is not included in the resulting changelog
    """
    ignored_commit_def = get_commit_def_of_conventional_commit(
        "chore: do not include me in the changelog",
        parser=default_conventional_parser,
    )

    # Because we are in init mode, the insertion flag is not present in the changelog
    # we must take it out manually because our repo generation fixture includes it automatically
    with changelog_md_file.open(newline=os.linesep) as rfd:
        # use os.linesep here because the insertion flag is os-specific
        # but convert the content to universal newlines for comparison
        expected_changelog_content = (
            rfd.read()
            .replace(f"{default_md_changelog_insertion_flag}{os.linesep}", "")
            .replace("\r", "")
        )

    # Set the project configurations
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.INIT.value
    )
    use_custom_parser(
        f"{CustomConventionalParserWithIgnorePatterns.__module__}:{CustomConventionalParserWithIgnorePatterns.__name__}"
    )

    # Setup: add the commit to be ignored
    repo_result["repo"].git.commit(m=ignored_commit_def["msg"], a=True)

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Take measurement after action
    actual_content = changelog_md_file.read_text()

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Verify that the changelog content does not include our commit
    assert ignored_commit_def["desc"] not in actual_content

    # Verify that the changelog content has not changed
    assert expected_changelog_content == actual_content
