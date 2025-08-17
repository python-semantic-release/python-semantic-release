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


cases = (
    # metadata release or pre-release should not affect partial tags
    (["--prerelease"], "0.0.0-rc.1", ["v0", "v0.0"], [], []),
    # Create partial tags when they don't exist
    (
        ["--minor", "--build-metadata", "build.12345"],
        "0.1.0+build.12345",
        [],
        ["v0", "v0.1", "v0.1.0"],
        [],
    ),
    (["--patch"], "0.0.1", [], ["v0", "v0.0"], []),
    (["--minor"], "0.1.0", [], ["v0", "v0.1"], []),
    (["--major"], "1.0.0", [], ["v1", "v1.0"], []),
    # Update existing partial tags
    (
        ["--patch", "--build-metadata", "build.12345"],
        "0.1.1+build.12345",
        ["v0", "v0.0", "v0.1", "v0.1.0"],
        ["v0.1.1"],
        ["v0", "v0.1"],
    ),
    (["--patch"], "0.0.1", ["v0", "v0.0"], [], ["v0", "v0.0"]),
    (["--minor"], "0.1.0", ["v0", "v0.0", "v0.1"], [], ["v0", "v0.1"]),
    (
        ["--major"],
        "1.0.0",
        ["v0", "v0.0", "v0.1", "v1", "v1.0"],
        [],
        ["v1", "v1.0"],
    ),
    # Update existing partial tags and create new one
    (["--minor"], "0.1.0", ["v0", "v0.0"], ["v0.1"], ["v0"]),
    # Partial tag disabled for older version, now enabled
    (
        ["--patch", "--build-metadata", "build.12345"],
        "1.1.2+build.12345",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1+build.1234"],
        ["v1", "v1.1", "v1.1.2"],
        [],
    ),
    (
        ["--patch"],
        "1.1.2",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v1", "v1.1"],
        [],
    ),
    (
        ["--minor"],
        "1.2.0",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v1", "v1.2"],
        [],
    ),
    (
        ["--major"],
        "2.0.0",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v2", "v2.0"],
        [],
    ),
)

cases_ids = [
    "metadata-release-or-pre-release",
    "create-partial-tags-when-they-dont-exist__build-metadata",
    "create-partial-tags-when-they-dont-exist__patch",
    "create-partial-tags-when-they-dont-exist__minor",
    "create-partial-tags-when-they-dont-exist__major",
    "update-existing-partial-tags__build-metadata",
    "update-existing-partial-tags__patch",
    "update-existing-partial-tags__minor",
    "update-existing-partial-tags__major",
    "update-existing-partial-tags-and-create-new-one",
    "partial-tag-disabled-for-older-version__build-metadata",
    "partial-tag-disabled-for-older-version__patch",
    "partial-tag-disabled-for-older-version__minor",
    "partial-tag-enabled-for-newer-version__major",
]


@pytest.mark.parametrize(
    "repo_result, add_partial_tags, cli_args, next_release_version, existing_partial_tags, expected_new_partial_tags, expected_moved_partial_tags",
    [
        *(
            (
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                True,
                cli_args,
                next_release_version,
                existing_tags,
                expected_new_partial_tags,
                expected_moved_partial_tags,
            )
            for cli_args, next_release_version, existing_tags, expected_new_partial_tags, expected_moved_partial_tags in cases
        ),
        *(
            (
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                False,
                cli_args,
                next_release_version,
                existing_tags,
                expected_new_partial_tags,
                expected_moved_partial_tags,
            )
            for cli_args, next_release_version, existing_tags, expected_new_partial_tags, expected_moved_partial_tags in cases
        ),
    ],
    ids=[f"{case_id}__partial-tags-enabled" for case_id in cases_ids]
    + [f"{case_id}__partial-tags-disabled" for case_id in cases_ids],
)
def test_version_partial_tag_creation(
    repo_result: BuiltRepoResult,
    add_partial_tags: bool,
    cli_args: list[str],
    next_release_version: str,
    example_project_dir: ExProjectDir,
    example_pyproject_toml: Path,
    existing_partial_tags: list[str],
    expected_new_partial_tags: list[str],
    expected_moved_partial_tags: list[str],
    cli_runner: CliRunner,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """Test that the version creates the expected partial tags."""
    # Enable partial tags
    update_pyproject_toml("tool.semantic_release.add_partial_tags", add_partial_tags)

    repo = repo_result["repo"]
    version_file = example_project_dir.joinpath(
        "src", EXAMPLE_PROJECT_NAME, "_version.py"
    )
    expected_changed_files = sorted(
        [
            "CHANGELOG.md",
            "pyproject.toml",
            str(version_file.relative_to(example_project_dir)),
        ]
    )
    expected_new_partial_tags = expected_new_partial_tags if add_partial_tags else []
    expected_moved_partial_tags = (
        expected_moved_partial_tags if add_partial_tags else []
    )

    # Setup: create existing tags
    for tag in existing_partial_tags:
        repo.create_tag(tag)

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name: repo.commit(tag) for tag in repo.tags}
    version_py_before = dynamic_python_import(
        version_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    pyproject_toml_before = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )

    # Modify the pyproject.toml to remove the version so we can compare it later
    pyproject_toml_before.get("tool", {}).get("poetry").pop("version")  # type: ignore[attr-defined]

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
    result = cli_runner.invoke(main, cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name: repo.commit(tag) for tag in repo.tags}
    new_tags = {tag: sha for tag, sha in tags_after.items() if tag not in tags_before}
    moved_tags = {
        tag: sha
        for tag, sha in tags_after.items()
        if tag in tags_before and sha != tags_before[tag]
    }
    differing_files = [
        # Make sure filepath uses os specific path separators
        str(Path(file))
        for file in str(repo.git.diff("HEAD", "HEAD~1", name_only=True)).splitlines()
    ]
    pyproject_toml_after = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    pyproj_version_after = (
        pyproject_toml_after.get("tool", {}).get("poetry", {}).pop("version")
    )

    # Load python module for reading the version (ensures the file is valid)
    version_py_after = dynamic_python_import(
        version_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    #
    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    # A version tag and the expected partial tag have been created
    assert len(new_tags) == 1 + len(expected_new_partial_tags)
    assert len(moved_tags) == len(expected_moved_partial_tags)
    assert f"v{next_release_version}" in new_tags
    # Check that all new tags and moved tags are present and on the head commit
    for partial_tag in expected_new_partial_tags:
        assert partial_tag in new_tags
        assert repo.commit(partial_tag).hexsha == head_after.hexsha
    for partial_tag in expected_moved_partial_tags:
        assert partial_tag in moved_tags
        assert repo.commit(partial_tag).hexsha == head_after.hexsha

    # 1 for commit, 1 for tag, 1 for each moved or created partial tag
    assert mocked_git_push.call_count == 2 + len(expected_new_partial_tags) + len(
        expected_moved_partial_tags
    )
    assert post_mocker.call_count == 1  # vcs release creation occurred

    # Changelog already reflects changes this should introduce
    assert expected_changed_files == differing_files

    # Compare pyproject.toml
    assert pyproject_toml_before == pyproject_toml_after
    assert next_release_version == pyproj_version_after

    # Compare _version.py
    assert next_release_version == version_py_after
    assert version_py_before != version_py_after
