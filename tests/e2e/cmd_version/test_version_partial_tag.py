from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import tomlkit

# Limitation in pytest-lazy-fixture - see https://stackoverflow.com/a/69884019
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.commands.main import main

from tests.const import EXAMPLE_PROJECT_NAME, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures import (
    repo_w_no_tags_conventional_commits,
)
from tests.util import (
    assert_successful_exit_code,
    dynamic_python_import,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from click.testing import CliRunner
    from requests_mock import Mocker

    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult



@pytest.mark.parametrize(
    "repo_result, cli_args, next_release_version, existing_partial_tags, expected_new_partial_tags, expected_moved_partial_tags",
    [
        *(
            (
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                cli_args,
                next_release_version,
                existing_partial_tags,
                expected_new_partial_tags,
                expected_moved_partial_tags,
            )
            for cli_args, next_release_version, existing_partial_tags, expected_new_partial_tags, expected_moved_partial_tags in (
                # metadata release or pre-release should not affect partial tags
                (["--build-metadata", "build.12345"], "0.1.0+build.12345", ["v0", "v0.0"], [], []),
                (["--prerelease"], "0.0.0-rc.1", ["v0", "v0.0"], [], []),
                # Create partial tags when they don't exist
                (["--patch"], "0.0.1", [], ["v0", "v0.0"], []),
                (["--minor"], "0.1.0", [], ["v0", "v0.1"], []),
                (["--major"], "1.0.0", [], ["v1", "v1.0"], []),
                # Update existing partial tags
                (["--patch"], "0.0.1", ["v0", "v0.0"], [], ["v0", "v0.0"]),
                (["--minor"], "0.1.0", ["v0", "v0.0", "v0.1"], [], ["v0", "v0.1"]),
                (["--major"], "1.0.0", ["v0", "v0.0", "v0.1", "v1", "v1.0"], [], ["v1", "v1.0"]),
                # Update existing partial tags and create new one
                (["--minor"], "0.1.0", ["v0", "v0.0"], ["v0.1"], ["v0"]),
            )
        )
    ],
)
def test_version_partial_tag_creation(
    repo_result: BuiltRepoResult,
    cli_args: list[str],
    next_release_version: str,
    existing_partial_tags: list[str],
    expected_new_partial_tags: list[str],
    expected_moved_partial_tags: list[str],
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """Test that the version creates the expected partial tags."""
    repo = repo_result["repo"]

    # Setup: create existing tags
    for tag in existing_partial_tags:
        repo.create_tag(tag)

    # Setup: take measurement before running the version command
    tags_before = {tag.name: repo.commit(tag) for tag in repo.tags}

    # Enable partial tags
    update_pyproject_toml("tool.semantic_release.add_partial_tags", True)

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name: repo.commit(tag) for tag in repo.tags}
    new_tags = {tag: sha for tag, sha in tags_after.items() if tag not in tags_before}
    moved_tags = {tag: sha for tag, sha in tags_after.items() if tag in tags_before and sha != tags_before[tag]}
    #
    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A version tag and the expected partial tag have been created
    assert len(new_tags) == 1 + len(expected_new_partial_tags)
    assert len(moved_tags) == len(expected_moved_partial_tags)
    assert f"v{next_release_version}" in new_tags
    for partial_tag in expected_new_partial_tags:
        assert partial_tag in new_tags
    for partial_tag in expected_moved_partial_tags:
        assert partial_tag in moved_tags

    # Check that all new tags and moved tags are on the head commit
    for tag, sha in {**new_tags, **moved_tags}.items():
        assert repo.commit(tag).hexsha == head_after.hexsha

    # 1 for commit, 1 for tag, 1 for each moved or created partial tag
    assert mocked_git_push.call_count == 2 + len(expected_new_partial_tags) + len(expected_moved_partial_tags)
    assert post_mocker.call_count == 1  # vcs release creation occurred
