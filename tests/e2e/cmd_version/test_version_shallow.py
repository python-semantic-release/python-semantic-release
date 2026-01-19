"""Tests for version command with shallow repositories."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from git import Repo
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs.github import Github

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.example_project import change_to_ex_proj_dir
from tests.fixtures.repos import repo_w_trunk_only_conventional_commits
from tests.fixtures.repos.trunk_based_dev.repo_w_tags import (
    build_trunk_only_repo_w_tags,
)
from tests.util import assert_successful_exit_code, temporary_working_directory

if TYPE_CHECKING:
    from requests_mock import Mocker

    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import ExProjectDir, UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import (
        BuildSpecificRepoFn,
        CommitConvention,
        GetCfgValueFromDefFn,
        GetGitRepo4DirFn,
        GetVersionsFromRepoBuildDefFn,
    )


@pytest.mark.parametrize(
    "repo_fixture_name, build_repo_fn",
    [
        (
            repo_fixture_name,
            lazy_fixture(build_repo_fn_name),
        )
        for repo_fixture_name, build_repo_fn_name in [
            (
                repo_w_trunk_only_conventional_commits.__name__,
                build_trunk_only_repo_w_tags.__name__,
            ),
        ]
    ],
)
@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_version_w_shallow_repo_unshallows(
    repo_fixture_name: str,
    run_cli: RunCliFn,
    build_repo_fn: BuildSpecificRepoFn,
    example_project_dir: ExProjectDir,
    git_repo_for_directory: GetGitRepo4DirFn,
    post_mocker: Mocker,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """
    Test that the version command automatically unshallows a shallow repository.

    Given a shallow repository,
    When running the version command,
    Then the repository should be unshallowed and release should succeed
    """
    remote_name = "origin"

    # Create a bare remote (simulating origin)
    local_origin = Repo.init(str(example_project_dir / "local_origin"), bare=True)

    # build target repo into a temporary directory
    target_repo_dir = example_project_dir / repo_fixture_name
    commit_type: CommitConvention = (
        repo_fixture_name.split("commits", 1)[0].split("_")[-2]  # type: ignore[assignment]
    )
    target_repo_definition = build_repo_fn(
        repo_name=repo_fixture_name,
        commit_type=commit_type,
        dest_dir=target_repo_dir,
    )
    target_git_repo = git_repo_for_directory(target_repo_dir)

    # Configure the source repo to use the bare remote (removing any existing 'origin')
    with suppress(AttributeError):
        target_git_repo.delete_remote(target_git_repo.remotes[remote_name])

    target_git_repo.create_remote(remote_name, str(local_origin.working_dir))

    # Remove last release before pushing to upstream
    tag_format_str = cast(
        "str", get_cfg_value_from_def(target_repo_definition, "tag_format_str")
    )
    latest_tag = tag_format_str.format(
        version=get_versions_from_repo_build_def(target_repo_definition)[-1]
    )
    target_git_repo.git.tag("-d", latest_tag)
    target_git_repo.git.reset("--hard", "HEAD~1")

    # TODO: when available, switch this to use hvcs=none or similar config to avoid token use for push
    update_pyproject_toml(
        "tool.semantic_release.remote.ignore_token_for_push",
        True,
        target_repo_dir / pyproject_toml_file,
    )
    target_git_repo.git.commit(amend=True, no_edit=True, all=True)

    # push the current state to establish the remote (cannot push tags and branches at the same time)
    target_git_repo.git.push(remote_name, all=True)  # all branches
    target_git_repo.git.push(remote_name, tags=True)  # all tags

    # ensure bare remote HEAD points to the active branch so clones can checkout
    local_origin.git.symbolic_ref(
        "HEAD", f"refs/heads/{target_git_repo.active_branch.name}"
    )

    # current remote tags
    remote_origin_tags_before = {tag.name for tag in local_origin.tags}

    # Create a shallow clone from the remote using file:// protocol for depth support
    shallow_repo = Repo.clone_from(
        f"file://{local_origin.working_dir}",
        str(example_project_dir / "shallow_clone"),
        no_local=True,
        depth=1,
    )
    with shallow_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    with shallow_repo:
        # Verify it's a shallow clone
        shallow_file = Path(shallow_repo.git_dir, "shallow")
        assert shallow_file.exists(), "Repository should be shallow"

    # Capture expected values from the full repo
    expected_vcs_url_post = 1
    commit_sha_before = shallow_repo.head.commit.hexsha

    # Run PSR on the shallow clone
    with temporary_working_directory(str(shallow_repo.working_dir)):
        cli_cmd = [MAIN_PROG_NAME, VERSION_SUBCMD, "--patch"]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # Initial execution check
    assert_successful_exit_code(result, cli_cmd)

    # Take measurements after running PSR
    remote_origin_tags_after = {tag.name for tag in local_origin.tags}
    different_tags = remote_origin_tags_after.difference(remote_origin_tags_before)
    with shallow_repo:
        parent_commit_shas = [
            parent.hexsha for parent in shallow_repo.head.commit.parents
        ]
        commit_sha_after = shallow_repo.head.commit.hexsha

    # Verify the shallow file is gone (repo was unshallowed)
    assert not shallow_file.exists(), "Repository should be unshallowed"

    # Verify release was successful
    assert commit_sha_before != commit_sha_after, "Expected commit SHA to change"
    assert (
        commit_sha_before in parent_commit_shas
    ), "Expected new commit to be created on HEAD"
    assert (
        latest_tag in different_tags
    ), "Expected a new tag to be created and pushed to remote"
    assert expected_vcs_url_post == post_mocker.call_count  # 1x vcs release created


@pytest.mark.parametrize(
    "repo_fixture_name, build_repo_fn",
    [
        (
            repo_fixture_name,
            lazy_fixture(build_repo_fn_name),
        )
        for repo_fixture_name, build_repo_fn_name in [
            (
                repo_w_trunk_only_conventional_commits.__name__,
                build_trunk_only_repo_w_tags.__name__,
            ),
        ]
    ],
)
@pytest.mark.usefixtures(change_to_ex_proj_dir.__name__)
def test_version_noop_w_shallow_repo(
    repo_fixture_name: str,
    run_cli: RunCliFn,
    build_repo_fn: BuildSpecificRepoFn,
    example_project_dir: ExProjectDir,
    git_repo_for_directory: GetGitRepo4DirFn,
    post_mocker: Mocker,
    get_cfg_value_from_def: GetCfgValueFromDefFn,
    get_versions_from_repo_build_def: GetVersionsFromRepoBuildDefFn,
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> None:
    """
    Test that the version command in noop mode reports unshallow action.

    Given a shallow repository,
    When running the version command with --noop,
    Then the command should report what it would do but not actually unshallow
    """
    remote_name = "origin"

    # Create a bare remote (simulating origin)
    local_origin = Repo.init(str(example_project_dir / "local_origin"), bare=True)

    # build target repo into a temporary directory
    target_repo_dir = example_project_dir / repo_fixture_name
    commit_type: CommitConvention = (
        repo_fixture_name.split("commits", 1)[0].split("_")[-2]  # type: ignore[assignment]
    )
    target_repo_definition = build_repo_fn(
        repo_name=repo_fixture_name,
        commit_type=commit_type,
        dest_dir=target_repo_dir,
    )
    target_git_repo = git_repo_for_directory(target_repo_dir)

    # Configure the source repo to use the bare remote (removing any existing 'origin')
    with suppress(AttributeError):
        target_git_repo.delete_remote(target_git_repo.remotes[remote_name])

    target_git_repo.create_remote(remote_name, str(local_origin.working_dir))

    # Remove last release before pushing to upstream
    tag_format_str = cast(
        "str", get_cfg_value_from_def(target_repo_definition, "tag_format_str")
    )
    latest_tag = tag_format_str.format(
        version=get_versions_from_repo_build_def(target_repo_definition)[-1]
    )
    target_git_repo.git.tag("-d", latest_tag)
    target_git_repo.git.reset("--hard", "HEAD~1")

    # TODO: when available, switch this to use hvcs=none or similar config to avoid token use for push
    update_pyproject_toml(
        "tool.semantic_release.remote.ignore_token_for_push",
        True,
        target_repo_dir / pyproject_toml_file,
    )
    target_git_repo.git.commit(amend=True, no_edit=True, all=True)

    # push the current state to establish the remote (cannot push tags and branches at the same time)
    target_git_repo.git.push(remote_name, all=True)  # all branches
    target_git_repo.git.push(remote_name, tags=True)  # all tags

    # ensure bare remote HEAD points to the active branch so clones can checkout
    local_origin.git.symbolic_ref(
        "HEAD", f"refs/heads/{target_git_repo.active_branch.name}"
    )

    # Create a shallow clone from the remote using file:// protocol for depth support
    shallow_repo = Repo.clone_from(
        f"file://{local_origin.working_dir}",
        str(example_project_dir / "shallow_clone"),
        no_local=True,
        depth=1,
    )
    with shallow_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    with shallow_repo:
        # Verify it's a shallow clone
        shallow_file = Path(shallow_repo.git_dir, "shallow")
        assert shallow_file.exists(), "Repository should be shallow"

    # Capture expected values from the full repo
    expected_vcs_url_post = 0
    commit_sha_before = shallow_repo.head.commit.hexsha
    remote_origin_tags_before = {tag.name for tag in local_origin.tags}

    # Run PSR in noop mode on the shallow clone
    with temporary_working_directory(str(shallow_repo.working_dir)):
        cli_cmd = [MAIN_PROG_NAME, "--noop", VERSION_SUBCMD, "--patch"]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    # Initial execution check
    assert_successful_exit_code(result, cli_cmd)

    # Take measurements after running PSR
    remote_origin_tags_after = {tag.name for tag in local_origin.tags}
    different_tags = remote_origin_tags_after.difference(remote_origin_tags_before)
    with shallow_repo:
        commit_sha_after = shallow_repo.head.commit.hexsha

    # Verify the shallow file still exists (repo was NOT actually unshallowed in noop)
    assert shallow_file.exists(), "Repository should still be shallow in noop mode"

    # Verify no actual changes were made
    assert (
        commit_sha_before == commit_sha_after
    ), "Expected commit SHA to remain unchanged in noop mode"
    assert not different_tags, "Expected no new tags to be created in noop mode"
    assert expected_vcs_url_post == post_mocker.call_count
