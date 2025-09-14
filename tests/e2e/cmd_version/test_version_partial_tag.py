from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import tomlkit
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from tests.const import EXAMPLE_PROJECT_NAME, MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures import (
    repo_w_no_tags_conventional_commits,
)
from tests.util import (
    assert_successful_exit_code,
    dynamic_python_import,
)

if TYPE_CHECKING:
    from typing import List
    from unittest.mock import MagicMock

    from requests_mock import Mocker
    from typing_extensions import TypeAlias

    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import (
        ExProjectDir,
        GetExpectedVersionPyFileContentFn,
        UpdatePyprojectTomlFn,
    )
    from tests.fixtures.git_repo import BuiltRepoResult

    CaseId: TypeAlias = str
    CliArgs: TypeAlias = List[str]
    NextReleaseVersion: TypeAlias = str
    ExistingTags: TypeAlias = List[str]
    ExpectedNewPartialTags: TypeAlias = List[str]
    ExpectedMovedPartialTags: TypeAlias = List[str]


cases: tuple[
    tuple[
        CaseId,
        CliArgs,
        NextReleaseVersion,
        ExistingTags,
        ExpectedNewPartialTags,
        ExpectedMovedPartialTags,
    ],
    ...,
] = (
    # pre-release should not affect partial tags
    (
        "pre-release",
        ["--prerelease"],
        "0.0.0-rc.1",
        ["v0", "v0.0"],
        [],
        [],
    ),
    # Create partial tags when they don't exist
    (
        "create-partial-tags-when-they-dont-exist__build-metadata",
        ["--minor", "--build-metadata", "build.12345"],
        "0.1.0+build.12345",
        [],
        ["v0", "v0.1", "v0.1.0"],
        [],
    ),
    (
        "create-partial-tags-when-they-dont-exist__patch",
        ["--patch"],
        "0.0.1",
        [],
        ["v0", "v0.0"],
        [],
    ),
    (
        "create-partial-tags-when-they-dont-exist__minor",
        ["--minor"],
        "0.1.0",
        [],
        ["v0", "v0.1"],
        [],
    ),
    (
        "create-partial-tags-when-they-dont-exist__major",
        ["--major"],
        "1.0.0",
        [],
        ["v1", "v1.0"],
        [],
    ),
    # Update existing partial tags
    (
        "update-existing-partial-tags__build-metadata",
        ["--patch", "--build-metadata", "build.12345"],
        "0.1.1+build.12345",
        ["v0", "v0.0", "v0.1", "v0.1.0"],
        ["v0.1.1"],
        ["v0", "v0.1"],
    ),
    (
        "update-existing-partial-tags__patch",
        ["--patch"],
        "0.0.1",
        ["v0", "v0.0"],
        [],
        ["v0", "v0.0"],
    ),
    (
        "update-existing-partial-tags__minor",
        ["--minor"],
        "0.1.0",
        ["v0", "v0.0", "v0.1"],
        [],
        ["v0", "v0.1"],
    ),
    (
        "update-existing-partial-tags__major",
        ["--major"],
        "1.0.0",
        ["v0", "v0.0", "v0.1", "v1", "v1.0"],
        [],
        ["v1", "v1.0"],
    ),
    # Update existing partial tags and create new one
    (
        "update-existing-partial-tags-and-create-new-one",
        ["--minor"],
        "0.1.0",
        ["v0", "v0.0"],
        ["v0.1"],
        ["v0"],
    ),
    # Partial tag disabled for older version, now enabled
    (
        "partial-tag-disabled-for-older-version__build-metadata",
        ["--patch", "--build-metadata", "build.12345"],
        "1.1.2+build.12345",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1+build.1234"],
        ["v1", "v1.1", "v1.1.2"],
        [],
    ),
    (
        "partial-tag-disabled-for-older-version__patch",
        ["--patch"],
        "1.1.2",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v1", "v1.1"],
        [],
    ),
    (
        "partial-tag-disabled-for-older-version__minor",
        ["--minor"],
        "1.2.0",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v1", "v1.2"],
        [],
    ),
    (
        "partial-tag-enabled-for-newer-version__major",
        ["--major"],
        "2.0.0",
        ["v0.1.0", "v0.1.1", "v1.0.0", "v1.1.0", "v1.1.1"],
        ["v2", "v2.0"],
        [],
    ),
)


@pytest.mark.parametrize(
    "repo_result, add_partial_tags, cli_args, next_release_version, existing_partial_tags, expected_new_partial_tags, expected_moved_partial_tags",
    [
        *(
            pytest.param(
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                True,
                cli_args,
                next_release_version,
                existing_tags,
                expected_new_partial_tags,
                expected_moved_partial_tags,
                id=f"{case_id}__partial-tags-enabled",
            )
            for case_id, cli_args, next_release_version, existing_tags, expected_new_partial_tags, expected_moved_partial_tags in cases
        ),
        *(
            pytest.param(
                lazy_fixture(repo_w_no_tags_conventional_commits.__name__),
                False,
                cli_args,
                next_release_version,
                existing_tags,
                expected_new_partial_tags,
                expected_moved_partial_tags,
                id=f"{case_id}__partial-tags-disabled",
            )
            for case_id, cli_args, next_release_version, existing_tags, expected_new_partial_tags, expected_moved_partial_tags in cases
        ),
    ],
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
    run_cli: RunCliFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_file: Path,
    changelog_md_file: Path,
    version_py_file: Path,
    get_expected_version_py_file_content: GetExpectedVersionPyFileContentFn,
):
    # Force clean directory state before test (needed for the repo_w_no_tags)
    repo = repo_result["repo"]
    repo.git.reset("HEAD", hard=True)

    # Enable partial tags
    update_pyproject_toml("tool.semantic_release.add_partial_tags", add_partial_tags)

    expected_changed_files = sorted(
        [
            str(changelog_md_file),
            str(pyproject_toml_file),
            str(version_py_file),
        ]
    )
    expected_new_partial_tags = expected_new_partial_tags if add_partial_tags else []
    expected_moved_partial_tags = (
        expected_moved_partial_tags if add_partial_tags else []
    )

    expected_version_py_content = get_expected_version_py_file_content(
        next_release_version
    )

    # Setup: create existing tags
    for tag in existing_partial_tags:
        repo.create_tag(tag)

    # Setup: take measurement before running the version command
    head_sha_before = repo.head.commit.hexsha
    tags_before = {tag.name: repo.commit(tag) for tag in repo.tags}

    pyproject_toml_before = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )

    # Modify the pyproject.toml to remove the version so we can compare it later
    pyproject_toml_before.get("tool", {}).get("poetry", {}).pop("version", None)

    # Define expectations before execution (hypothesis)
    expected_git_fetch_calls = 1
    expected_vcs_release_calls = 1
    # 1 for commit, 1 for tag, 1 for each moved or created partial tag
    expected_git_push_calls = (
        2 + len(expected_new_partial_tags) + len(expected_moved_partial_tags)
    )

    # Act
    cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, *cli_args]
    result = run_cli(cli_cmd[1:])

    # take measurement after running the version command
    head_after = repo.head.commit
    tags_after = {tag.name: repo.commit(tag.name) for tag in repo.tags}
    new_tags = {tag: sha for tag, sha in tags_after.items() if tag not in tags_before}
    moved_tags = {
        tag: sha
        for tag, sha in tags_after.items()
        if tag in tags_before and sha != tags_before[tag]
    }
    differing_files = sorted(
        [
            # Make sure filepath uses os specific path separators
            str(Path(file))
            for file in str(
                repo.git.diff("HEAD", "HEAD~1", name_only=True)
            ).splitlines()
        ]
    )
    pyproject_toml_after = tomlkit.loads(
        example_pyproject_toml.read_text(encoding="utf-8")
    )
    pyproj_version_after = (
        pyproject_toml_after.get("tool", {}).get("poetry", {}).pop("version")
    )

    # Load python module for reading the version (ensures the file is valid)
    actual_version_py_content = (example_project_dir / version_py_file).read_text()

    # Evaluate (normal release actions should have occurred when forced patch bump)
    assert_successful_exit_code(result, cli_cmd)

    # A commit has been made
    assert [head_sha_before] == [head.hexsha for head in head_after.parents]

    # A version tag and the expected partial tag have been created
    assert 1 + len(expected_new_partial_tags) == len(new_tags)
    assert len(expected_moved_partial_tags) == len(moved_tags)
    assert f"v{next_release_version}" in new_tags

    # Check that all new tags and moved tags are present and on the head commit
    for partial_tag in expected_new_partial_tags:
        assert partial_tag in new_tags
        assert repo.commit(partial_tag).hexsha == head_after.hexsha

    for partial_tag in expected_moved_partial_tags:
        assert partial_tag in moved_tags
        assert repo.commit(partial_tag).hexsha == head_after.hexsha

    # Expected external calls
    assert (
        expected_git_fetch_calls == mocked_git_fetch.call_count
    )  # fetch occurred before push
    assert expected_git_push_calls == mocked_git_push.call_count
    assert (
        expected_vcs_release_calls == post_mocker.call_count
    )  # vcs release creation occurred

    # Changelog already reflects changes this should introduce
    assert expected_changed_files == differing_files

    # Compare pyproject.toml
    assert pyproject_toml_before == pyproject_toml_after
    assert next_release_version == pyproj_version_after

    # Compare _version.py
    assert expected_version_py_content == actual_version_py_content

    # Verify content is parsable & importable
    dynamic_version = dynamic_python_import(
        example_project_dir / version_py_file, f"{EXAMPLE_PROJECT_NAME}._version"
    ).__version__

    assert next_release_version == dynamic_version
