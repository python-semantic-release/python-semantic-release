"""Tests for the GitProject class."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from git import GitCommandError

import semantic_release.gitproject
from semantic_release.errors import (
    DetachedHeadGitError,
    GitFetchError,
    LocalGitError,
    UnknownUpstreamBranchError,
    UpstreamBranchChangedError,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator

    from semantic_release.gitproject import GitProject

    class MockGit(MagicMock):
        """A mock Git object that can be used in tests."""

        rev_parse: MagicMock
        fetch: MagicMock
        push: MagicMock

    class RepoMock(MagicMock):
        """A mock Git repository that can be used in tests."""

        active_branch: MagicMock
        remotes: dict[str, MagicMock]
        git: MockGit
        git_dir: str
        commit: MagicMock


@pytest.fixture
def mock_repo(tmp_path: Path) -> RepoMock:
    """Create a mock Git repository with proper structure for new implementation."""
    repo = cast("RepoMock", MagicMock())

    repo.git_dir = str(tmp_path / ".git")

    # Mock active branch
    active_branch = MagicMock()
    active_branch.name = "main"

    # Mock tracking branch
    tracking_branch = MagicMock()
    tracking_branch.name = "origin/main"
    active_branch.tracking_branch = MagicMock(return_value=tracking_branch)

    repo.active_branch = active_branch

    # Mock remotes
    remote_obj = MagicMock()
    remote_obj.fetch = MagicMock()

    # Mock refs for the remote
    ref_obj = MagicMock()
    commit_obj = MagicMock()
    commit_obj.hexsha = "abc123"
    ref_obj.commit = commit_obj

    remote_obj.refs = {"main": ref_obj}
    repo.remotes = {"origin": remote_obj}

    # Mock git.rev_parse
    repo.git = MagicMock()
    repo.git.rev_parse = MagicMock(return_value="abc123")

    # Ensure repo.commit returns a commit-like object with the expected hexsha
    # and no parents so that comparisons in verify_upstream_unchanged succeed.
    commit_obj.iter_parents = MagicMock(return_value=[])
    repo.commit = MagicMock(return_value=commit_obj)

    return repo


@pytest.fixture
def git_project(tmp_path: Path) -> GitProject:
    """Create a GitProject instance for testing."""
    return semantic_release.gitproject.GitProject(directory=tmp_path)


@pytest.fixture
def mock_gitproject(
    git_project: GitProject, mock_repo: RepoMock
) -> Generator[GitProject, None, None]:
    """Patch the GitProject to use the mock Repo."""
    module_path = semantic_release.gitproject.__name__
    with patch(f"{module_path}.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)
        yield git_project


def test_verify_upstream_unchanged_success(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged succeeds when upstream has not changed."""
    # Should not raise an exception
    mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)

    # Verify fetch was called
    mock_repo.remotes["origin"].fetch.assert_called_once()
    # Verify rev_parse was called for HEAD
    mock_repo.git.rev_parse.assert_called_once_with("HEAD")


def test_verify_upstream_unchanged_fails_when_changed(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises error when upstream has changed."""
    # Mock git operations with different SHAs
    mock_repo.git.rev_parse = MagicMock(
        return_value="def456"  # Different from upstream
    )

    # Ensure repo.commit returns a commit-like object with the different hexsha
    changed_commit = MagicMock()
    changed_commit.hexsha = "def456"
    changed_commit.iter_parents = MagicMock(return_value=[])
    mock_repo.commit = MagicMock(return_value=changed_commit)

    with pytest.raises(
        UpstreamBranchChangedError, match=r"Upstream branch .* has changed"
    ):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_noop(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged does nothing in noop mode."""
    # Should not raise an exception and should not call git operations
    mock_gitproject.verify_upstream_unchanged(noop=True)

    # Verify Repo was not instantiated at all in noop mode
    mock_repo.assert_not_called()


def test_verify_upstream_unchanged_no_tracking_branch(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises error when no tracking branch exists."""
    # Mock no tracking branch
    mock_repo.active_branch.tracking_branch = MagicMock(return_value=None)

    # Should raise UnknownUpstreamBranchError
    with pytest.raises(UnknownUpstreamBranchError, match="No upstream branch found"):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_detached_head(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises error in detached HEAD state."""
    # Simulate detached HEAD by having active_branch raise TypeError
    # This is what GitPython does when in a detached HEAD state
    type(mock_repo).active_branch = PropertyMock(side_effect=TypeError("detached HEAD"))

    # Should raise DetachedHeadGitError
    with pytest.raises(DetachedHeadGitError, match="detached HEAD state"):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_fetch_fails(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises GitFetchError when fetch fails."""
    # Mock fetch to raise an error
    mock_repo.remotes["origin"].fetch = MagicMock(
        side_effect=GitCommandError("fetch", "error")
    )

    with pytest.raises(GitFetchError, match="Failed to fetch from remote"):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_upstream_sha_fails(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises error when upstream SHA cannot be determined."""
    # Mock refs to raise AttributeError (simulating missing branch)
    mock_repo.remotes["origin"].refs = MagicMock()
    mock_repo.remotes["origin"].refs.__getitem__ = MagicMock(
        side_effect=AttributeError("No such ref")
    )

    with pytest.raises(GitFetchError, match="Unable to determine upstream branch SHA"):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_local_ref_sha_fails(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged raises error when local ref SHA cannot be determined."""
    # Mock git operations - rev_parse fails
    mock_repo.git.rev_parse = MagicMock(
        side_effect=GitCommandError("rev-parse", "error")
    )

    with pytest.raises(
        LocalGitError,
        match="Unable to determine the SHA for local ref",
    ):
        mock_gitproject.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_with_custom_ref(
    mock_gitproject: GitProject, mock_repo: RepoMock
):
    """Test that verify_upstream_unchanged works with a custom ref like HEAD~1."""
    # Should not raise an exception
    mock_gitproject.verify_upstream_unchanged(local_ref="HEAD~1", noop=False)

    # Verify rev_parse was called with custom ref
    mock_repo.git.rev_parse.assert_called_once_with("HEAD~1")
