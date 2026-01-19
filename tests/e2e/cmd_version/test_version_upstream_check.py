"""E2E tests for upstream verification during version command."""

from __future__ import annotations

import contextlib
from pathlib import PureWindowsPath
from typing import TYPE_CHECKING, cast

import pytest
from git import Repo
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.hvcs.github import Github

from tests.const import MAIN_PROG_NAME, VERSION_SUBCMD
from tests.fixtures.example_project import change_to_ex_proj_dir
from tests.fixtures.repos.trunk_based_dev import (
    repo_w_trunk_only_conventional_commits,
)
from tests.fixtures.repos.trunk_based_dev.repo_w_tags import (
    build_trunk_only_repo_w_tags,
)
from tests.util import (
    add_text_to_file,
    assert_exit_code,
    assert_successful_exit_code,
    temporary_working_directory,
)

if TYPE_CHECKING:
    from pathlib import Path

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
def test_version_upstream_check_success_no_changes(
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
):
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
    with contextlib.suppress(AttributeError):
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

    # Clone the repo to simulate a local workspace
    test_repo = Repo.clone_from(
        f"file://{local_origin.working_dir}",
        str(example_project_dir / "repo_clone"),
        no_local=True,
    )
    with test_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    current_head_sha = test_repo.head.commit.hexsha

    # Act: run PSR on the cloned repo - it should verify upstream and succeed
    with temporary_working_directory(str(test_repo.working_dir)):
        cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    remote_origin_tags_after = {tag.name for tag in local_origin.tags}

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Verify release occurred as expected
    with test_repo:
        assert latest_tag in test_repo.tags, "Expected release tag to be created"
        assert current_head_sha in [
            parent.hexsha for parent in test_repo.head.commit.parents
        ], "Expected new commit to be created on HEAD"
        different_tags = remote_origin_tags_after.difference(remote_origin_tags_before)
        assert latest_tag in different_tags, "Expected new tag to be pushed to remote"

    # Verify VCS release was created
    expected_vcs_url_post = 1
    assert expected_vcs_url_post == post_mocker.call_count  # one vcs release created


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
def test_version_upstream_check_success_no_changes_untracked_branch(
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
):
    """Test that PSR succeeds when the upstream branch is untracked but unchanged."""
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
    with contextlib.suppress(AttributeError):
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

    # Simulate CI environment after someone pushes to the repo
    ci_commit_sha = target_git_repo.head.commit.hexsha
    ci_branch = target_git_repo.active_branch.name

    # current remote tags
    remote_origin_tags_before = {tag.name for tag in local_origin.tags}

    # Simulate a CI environment by fetching the repo to a new location
    test_repo = Repo.init(str(example_project_dir / "ci_repo"))
    with test_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    # Configure and retrieve the repository (see GitHub actions/checkout@v5)
    test_repo.git.remote(
        "add",
        remote_name,
        f"file:///{PureWindowsPath(local_origin.working_dir).as_posix()}",
    )
    test_repo.git.fetch("--depth=1", remote_name, ci_commit_sha)

    # Simulate CI environment and recommended workflow (in docs)
    # NOTE: this could be done in 1 step, but most CI pipelines are doing it in 2 steps
    # 1. Checkout the commit sha (detached head)
    test_repo.git.checkout(ci_commit_sha, force=True)
    # 2. Forcefully set the branch to the current detached head
    test_repo.git.checkout("-B", ci_branch)

    # Act: run PSR on the cloned repo - it should verify upstream and succeed
    with temporary_working_directory(str(test_repo.working_dir)):
        cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    remote_origin_tags_after = {tag.name for tag in local_origin.tags}

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Verify release occurred as expected
    with test_repo:
        assert latest_tag in test_repo.tags, "Expected release tag to be created"
        assert ci_commit_sha in [
            parent.hexsha for parent in test_repo.head.commit.parents
        ], "Expected new commit to be created on HEAD"
        different_tags = remote_origin_tags_after.difference(remote_origin_tags_before)
        assert latest_tag in different_tags, "Expected new tag to be pushed to remote"

    # Verify VCS release was created
    expected_vcs_url_post = 1
    assert expected_vcs_url_post == post_mocker.call_count  # one vcs release created


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
def test_version_no_upstream_check_on_no_version_commit(
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
):
    """
    Test that PSR succeeds when no version commit is needed, so the upstream check is skipped.

    This replicates the scenario that occurred on python-semantic-release/publish-action@v10.5.1
    where the version command was run and no version commit was needed, but it failed because
    it attempted to check the upstream branch anyway and we hard coded HEAD~1 because it expects
    a version commit to be created. This is the only reason why you would check the upstream branch
    because pushing a tag to the remote can happen even if the upstream branch has changed.
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
    with contextlib.suppress(AttributeError):
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

    # Remove any version variables to ensure no version commit is needed
    update_pyproject_toml(
        "tool.semantic_release.version_variables",
        None,
        target_repo_dir / pyproject_toml_file,
    )
    update_pyproject_toml(
        "tool.semantic_release.version_toml",
        None,
        target_repo_dir / pyproject_toml_file,
    )
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

    # Simulate CI environment after someone pushes to the repo
    ci_commit_sha = target_git_repo.head.commit.hexsha
    ci_branch = target_git_repo.active_branch.name

    # current remote tags
    remote_origin_tags_before = {tag.name for tag in local_origin.tags}

    # Simulate a CI environment by fetching the repo to a new location
    test_repo = Repo.init(str(example_project_dir / "ci_repo"))
    with test_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    # Configure and retrieve the repository (see GitHub actions/checkout@v5)
    test_repo.git.remote(
        "add",
        remote_name,
        f"file:///{PureWindowsPath(local_origin.working_dir).as_posix()}",
    )
    test_repo.git.fetch("--depth=1", remote_name, ci_commit_sha)

    # Simulate CI environment and recommended workflow (in docs)
    # NOTE: this could be done in 1 step, but most CI pipelines are doing it in 2 steps
    # 1. Checkout the commit sha (detached head)
    test_repo.git.checkout(ci_commit_sha, force=True)
    # 2. Forcefully set the branch to the current detached head
    test_repo.git.checkout("-B", ci_branch)

    # Act: run PSR on the cloned repo - it should verify upstream and succeed
    with temporary_working_directory(str(test_repo.working_dir)):
        # We don't use `--no-commit` here because we want to test that the upstream check is skipped
        # when PSR determines that no version commit is needed. If we used `--no-commit`, it would skip the
        # upstream check because it would think that a version commit was not needed.
        cli_cmd = [
            MAIN_PROG_NAME,
            "--strict",
            VERSION_SUBCMD,
            "--no-changelog",
            "--skip-build",
        ]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    remote_origin_tags_after = {tag.name for tag in local_origin.tags}

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)

    # Verify release occurred as expected
    with test_repo:
        assert latest_tag in test_repo.tags, "Expected release tag to be created"
        assert (
            ci_commit_sha == test_repo.head.commit.hexsha
        ), "Expected no new commit to be created on HEAD"
        different_tags = remote_origin_tags_after.difference(remote_origin_tags_before)
        assert latest_tag in different_tags, "Expected new tag to be pushed to remote"

    # Verify VCS release was created
    expected_vcs_url_post = 1
    assert expected_vcs_url_post == post_mocker.call_count  # one vcs release created


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
def test_version_upstream_check_fails_when_upstream_changed(
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
    file_in_repo: str,
):
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
    with contextlib.suppress(AttributeError):
        target_git_repo.delete_remote(target_git_repo.remotes[remote_name])

    target_git_repo.create_remote(remote_name, f"file://{local_origin.working_dir}")

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

    # ensure bare remote HEAD points to the branch name used in the pushed repo
    local_origin.git.symbolic_ref(
        "HEAD", f"refs/heads/{target_git_repo.active_branch.name}"
    )

    # current remote tags
    remote_origin_tags_before = {tag.name for tag in local_origin.tags}

    # Clone the repo to simulate a local workspace
    test_repo = Repo.clone_from(
        f"file://{local_origin.working_dir}",
        str(example_project_dir / "repo_clone"),
        no_local=True,
    )
    with test_repo.config_writer("repository") as config:
        config.set_value("core", "hookspath", "")
        config.set_value("commit", "gpgsign", False)
        config.set_value("tag", "gpgsign", False)

    # Apply new commit to the original repo to simulate another developer pushing to upstream
    add_text_to_file(target_git_repo, str(target_repo_dir / file_in_repo))
    target_git_repo.index.add([str(file_in_repo)])
    target_git_repo.index.commit("feat: upstream change by another developer")
    target_git_repo.git.push(remote_name, target_git_repo.active_branch.name)

    # Act: run PSR - it should detect upstream changed and fail
    with temporary_working_directory(str(test_repo.working_dir)):
        cli_cmd = [MAIN_PROG_NAME, "--strict", VERSION_SUBCMD]
        result = run_cli(cli_cmd[1:], env={Github.DEFAULT_ENV_TOKEN_NAME: "1234"})

    remote_origin_tags_after = {tag.name for tag in local_origin.tags}

    # Evaluate
    assert_exit_code(1, result, cli_cmd)
    expected_err_msg = (
        f"Upstream branch '{remote_name}/{test_repo.active_branch.name}' has changed!"
    )
    # Verify error message mentions upstream
    assert (
        expected_err_msg in result.stderr
    ), f"Expected '{expected_err_msg}' in error output, got: {result.stderr}"

    assert (
        remote_origin_tags_before == remote_origin_tags_after
    ), "Expected no new tags to be pushed to remote"

    # Verify no VCS release was created
    expected_vcs_url_post = 0
    assert expected_vcs_url_post == post_mocker.call_count  # no vcs release created
