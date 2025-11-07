from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from freezegun import freeze_time

from semantic_release.version.version import Version

from tests.const import RepoActionStep
from tests.fixtures.monorepos.trunk_based_dev import (
    monorepo_w_trunk_only_releases_conventional_commits,
)
from tests.util import temporary_working_directory

if TYPE_CHECKING:
    from typing import Literal, Sequence
    from unittest.mock import MagicMock

    from requests_mock import Mocker

    from tests.e2e.cmd_version.bump_version.conftest import (
        InitMirrorRepo4RebuildFn,
        RunPSReleaseFn,
    )
    from tests.e2e.conftest import GetSanitizedChangelogContentFn
    from tests.fixtures.example_project import ExProjectDir
    from tests.fixtures.git_repo import (
        BuildRepoFromDefinitionFn,
        BuildSpecificRepoFn,
        CommitConvention,
        GetGitRepo4DirFn,
        RepoActionConfigure,
        RepoActionConfigureMonorepo,
        RepoActionCreateMonorepo,
        RepoActionRelease,
        RepoActions,
        SplitRepoActionsByReleaseTagsFn,
    )


@pytest.mark.parametrize(
    "repo_fixture_name",
    [
        pytest.param(repo_fixture_name, marks=pytest.mark.comprehensive)
        for repo_fixture_name in [
            monorepo_w_trunk_only_releases_conventional_commits.__name__,
        ]
    ],
)
def test_trunk_monorepo_rebuild_1_channel(
    repo_fixture_name: str,
    run_psr_release: RunPSReleaseFn,
    build_trunk_only_monorepo_w_tags: BuildSpecificRepoFn,
    split_repo_actions_by_release_tags: SplitRepoActionsByReleaseTagsFn,
    init_mirror_repo_for_rebuild: InitMirrorRepo4RebuildFn,
    example_project_dir: ExProjectDir,
    git_repo_for_directory: GetGitRepo4DirFn,
    build_repo_from_definition: BuildRepoFromDefinitionFn,
    mocked_git_fetch: MagicMock,
    mocked_git_push: MagicMock,
    post_mocker: Mocker,
    get_sanitized_md_changelog_content: GetSanitizedChangelogContentFn,
    get_sanitized_rst_changelog_content: GetSanitizedChangelogContentFn,
    monorepo_pkg1_pyproject_toml_file: Path,
    monorepo_pkg2_pyproject_toml_file: Path,
    monorepo_pkg1_version_py_file: Path,
    monorepo_pkg2_version_py_file: Path,
    monorepo_pkg1_changelog_md_file: Path,
    monorepo_pkg2_changelog_md_file: Path,
    monorepo_pkg1_changelog_rst_file: Path,
    monorepo_pkg2_changelog_rst_file: Path,
):
    # build target repo into a temporary directory
    target_repo_dir = example_project_dir / repo_fixture_name
    commit_type = cast(
        "CommitConvention", repo_fixture_name.split("commits", 1)[0].split("_")[-2]
    )
    target_repo_definition = build_trunk_only_monorepo_w_tags(
        repo_name=repo_fixture_name,
        commit_type=commit_type,
        dest_dir=target_repo_dir,
    )
    target_git_repo = git_repo_for_directory(target_repo_dir)

    # split repo actions by release actions
    release_tags_2_steps = split_repo_actions_by_release_tags(target_repo_definition)

    configuration_steps = cast(
        "Sequence[RepoActionConfigure | RepoActionCreateMonorepo | RepoActionConfigureMonorepo]",
        release_tags_2_steps.pop(None),
    )

    release_versions_2_steps = cast(
        "dict[Version | Literal['Unreleased'], list[RepoActions]]",
        release_tags_2_steps,
    )

    # Create the mirror repo directory
    mirror_repo_dir = init_mirror_repo_for_rebuild(
        mirror_repo_dir=(example_project_dir / "mirror"),
        configuration_steps=configuration_steps,
        files_to_remove=[],
    )

    mirror_git_repo = git_repo_for_directory(mirror_repo_dir)

    # rebuild repo from scratch stopping before each release tag
    for curr_release_key, steps in release_versions_2_steps.items():
        curr_release_str = (
            curr_release_key.as_tag()
            if isinstance(curr_release_key, Version)
            else curr_release_key
        )

        # make sure mocks are clear
        mocked_git_fetch.reset_mock()
        mocked_git_push.reset_mock()
        post_mocker.reset_mock()

        # Extract expected result from target repo
        if curr_release_str != "Unreleased":
            target_git_repo.git.checkout(curr_release_str, detach=True, force=True)

        expected_pkg1_md_changelog_content = get_sanitized_md_changelog_content(
            repo_dir=target_repo_dir, changelog_file=monorepo_pkg1_changelog_md_file
        )
        expected_pkg2_md_changelog_content = get_sanitized_md_changelog_content(
            repo_dir=target_repo_dir, changelog_file=monorepo_pkg2_changelog_md_file
        )
        expected_pkg1_rst_changelog_content = get_sanitized_rst_changelog_content(
            repo_dir=target_repo_dir, changelog_file=monorepo_pkg1_changelog_rst_file
        )
        expected_pkg2_rst_changelog_content = get_sanitized_rst_changelog_content(
            repo_dir=target_repo_dir, changelog_file=monorepo_pkg2_changelog_rst_file
        )
        expected_pkg1_pyproject_toml_content = (
            target_repo_dir / monorepo_pkg1_pyproject_toml_file
        ).read_text()
        expected_pkg2_pyproject_toml_content = (
            target_repo_dir / monorepo_pkg2_pyproject_toml_file
        ).read_text()
        expected_pkg1_version_file_content = (
            target_repo_dir / monorepo_pkg1_version_py_file
        ).read_text()
        expected_pkg2_version_file_content = (
            target_repo_dir / monorepo_pkg2_version_py_file
        ).read_text()
        expected_release_commit_text = target_git_repo.head.commit.message

        # In our repo env, start building the repo from the definition
        build_repo_from_definition(
            dest_dir=mirror_repo_dir,
            # stop before the release step
            repo_construction_steps=steps[
                : -1 if curr_release_str != "Unreleased" else None
            ],
        )

        release_directory = mirror_repo_dir

        for step in steps[::-1]:  # reverse order
            if step["action"] == RepoActionStep.CHANGE_DIRECTORY:
                release_directory = (
                    mirror_repo_dir
                    if str(Path(step["details"]["directory"]))
                    == str(mirror_repo_dir.root)
                    else Path(step["details"]["directory"])
                )

                release_directory = (
                    mirror_repo_dir / release_directory
                    if not release_directory.is_absolute()
                    else release_directory
                )

                if mirror_repo_dir not in release_directory.parents:
                    release_directory = mirror_repo_dir

                break

        # Act: run PSR on the repo instead of the RELEASE step
        if curr_release_str != "Unreleased":
            release_action_step = cast("RepoActionRelease", steps[-1])

            with freeze_time(
                release_action_step["details"]["datetime"]
            ), temporary_working_directory(release_directory):
                run_psr_release(
                    next_version_str=release_action_step["details"]["version"],
                    git_repo=mirror_git_repo,
                    config_toml_path=Path("pyproject.toml"),
                )
        else:
            # run psr changelog command to validate changelog
            pass

        # take measurement after running the version command
        actual_release_commit_text = mirror_git_repo.head.commit.message
        actual_pkg1_pyproject_toml_content = (
            mirror_repo_dir / monorepo_pkg1_pyproject_toml_file
        ).read_text()
        actual_pkg2_pyproject_toml_content = (
            mirror_repo_dir / monorepo_pkg2_pyproject_toml_file
        ).read_text()
        actual_pkg1_version_file_content = (
            mirror_repo_dir / monorepo_pkg1_version_py_file
        ).read_text()
        actual_pkg2_version_file_content = (
            mirror_repo_dir / monorepo_pkg2_version_py_file
        ).read_text()
        actual_pkg1_md_changelog_content = get_sanitized_md_changelog_content(
            repo_dir=mirror_repo_dir, changelog_file=monorepo_pkg1_changelog_md_file
        )
        actual_pkg2_md_changelog_content = get_sanitized_md_changelog_content(
            repo_dir=mirror_repo_dir, changelog_file=monorepo_pkg2_changelog_md_file
        )
        actual_pkg1_rst_changelog_content = get_sanitized_rst_changelog_content(
            repo_dir=mirror_repo_dir, changelog_file=monorepo_pkg1_changelog_rst_file
        )
        actual_pkg2_rst_changelog_content = get_sanitized_rst_changelog_content(
            repo_dir=mirror_repo_dir, changelog_file=monorepo_pkg2_changelog_rst_file
        )

        # Evaluate (normal release actions should have occurred as expected)
        # ------------------------------------------------------------------
        # Make sure version file is updated
        assert (
            expected_pkg1_pyproject_toml_content == actual_pkg1_pyproject_toml_content
        )
        assert (
            expected_pkg2_pyproject_toml_content == actual_pkg2_pyproject_toml_content
        )
        assert expected_pkg1_version_file_content == actual_pkg1_version_file_content
        assert expected_pkg2_version_file_content == actual_pkg2_version_file_content

        # Make sure changelog is updated
        assert expected_pkg1_md_changelog_content == actual_pkg1_md_changelog_content
        assert expected_pkg2_md_changelog_content == actual_pkg2_md_changelog_content
        assert expected_pkg1_rst_changelog_content == actual_pkg1_rst_changelog_content
        assert expected_pkg2_rst_changelog_content == actual_pkg2_rst_changelog_content

        # Make sure commit is created
        assert expected_release_commit_text == actual_release_commit_text

        if curr_release_str != "Unreleased":
            # Make sure tag is created
            assert curr_release_str in [tag.name for tag in mirror_git_repo.tags]

        # Make sure publishing actions occurred
        assert (
            mocked_git_fetch.call_count == 1
        )  # fetch called to check for remote changes
        assert mocked_git_push.call_count == 2  # 1 for commit, 1 for tag
        assert post_mocker.call_count == 1  # vcs release creation occurred
