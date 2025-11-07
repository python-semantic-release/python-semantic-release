from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from git import GitCommandError

from semantic_release.errors import (
    DetachedHeadGitError,
    GitFetchError,
    LocalGitError,
    UnknownUpstreamBranchError,
    UpstreamBranchChangedError,
)
from semantic_release.gitproject import GitProject

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def mock_repo():
    """Create a mock Git repository with proper structure for new implementation."""
    repo = MagicMock()

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


def test_verify_upstream_unchanged_success(tmp_path: Path, mock_repo: MagicMock):
    """Test that verify_upstream_unchanged succeeds when upstream has not changed."""
    git_project = GitProject(directory=tmp_path)

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        # Should not raise an exception
        git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)

    # Verify fetch was called
    mock_repo.remotes["origin"].fetch.assert_called_once()
    # Verify rev_parse was called for HEAD
    mock_repo.git.rev_parse.assert_called_once_with("HEAD")


def test_verify_upstream_unchanged_fails_when_changed(
    tmp_path: Path, mock_repo: MagicMock
):
    """Test that verify_upstream_unchanged raises error when upstream has changed."""
    git_project = GitProject(directory=tmp_path)

    # Mock git operations with different SHAs
    mock_repo.git.rev_parse = MagicMock(
        return_value="def456"  # Different from upstream
    )

    # Ensure repo.commit returns a commit-like object with the different hexsha
    changed_commit = MagicMock()
    changed_commit.hexsha = "def456"
    changed_commit.iter_parents = MagicMock(return_value=[])
    mock_repo.commit = MagicMock(return_value=changed_commit)

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(
            UpstreamBranchChangedError, match=r"Upstream branch .* has changed"
        ):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_noop(tmp_path: Path):
    """Test that verify_upstream_unchanged does nothing in noop mode."""
    git_project = GitProject(directory=tmp_path)

    mock_repo = MagicMock()

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        # Should not raise an exception and should not call git operations
        git_project.verify_upstream_unchanged(noop=True)

    # Verify Repo was not instantiated at all in noop mode
    mock_repo_class.assert_not_called()


def test_verify_upstream_unchanged_no_tracking_branch(
    tmp_path: Path, mock_repo: MagicMock
):
    """Test that verify_upstream_unchanged raises error when no tracking branch exists."""
    git_project = GitProject(directory=tmp_path)

    # Mock no tracking branch
    mock_repo.active_branch.tracking_branch = MagicMock(return_value=None)

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        # Should raise UnknownUpstreamBranchError
        with pytest.raises(
            UnknownUpstreamBranchError, match="No upstream branch found"
        ):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_detached_head(tmp_path: Path):
    """Test that verify_upstream_unchanged raises error in detached HEAD state."""
    git_project = GitProject(directory=tmp_path)

    mock_repo = MagicMock()
    # Simulate detached HEAD by having active_branch raise TypeError
    # This is what GitPython does when in a detached HEAD state
    type(mock_repo).active_branch = PropertyMock(side_effect=TypeError("detached HEAD"))

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        # Should raise DetachedHeadGitError
        with pytest.raises(DetachedHeadGitError, match="detached HEAD state"):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_fetch_fails(tmp_path: Path, mock_repo: MagicMock):
    """Test that verify_upstream_unchanged raises GitFetchError when fetch fails."""
    git_project = GitProject(directory=tmp_path)

    # Mock fetch to raise an error
    mock_repo.remotes["origin"].fetch = MagicMock(
        side_effect=GitCommandError("fetch", "error")
    )

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(GitFetchError, match="Failed to fetch from remote"):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_upstream_sha_fails(
    tmp_path: Path, mock_repo: MagicMock
):
    """Test that verify_upstream_unchanged raises error when upstream SHA cannot be determined."""
    git_project = GitProject(directory=tmp_path)

    # Mock refs to raise AttributeError (simulating missing branch)
    mock_repo.remotes["origin"].refs = MagicMock()
    mock_repo.remotes["origin"].refs.__getitem__ = MagicMock(
        side_effect=AttributeError("No such ref")
    )

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(
            GitFetchError, match="Unable to determine upstream branch SHA"
        ):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_local_ref_sha_fails(
    tmp_path: Path, mock_repo: MagicMock
):
    """Test that verify_upstream_unchanged raises error when local ref SHA cannot be determined."""
    git_project = GitProject(directory=tmp_path)

    # Mock git operations - rev_parse fails
    mock_repo.git.rev_parse = MagicMock(
        side_effect=GitCommandError("rev-parse", "error")
    )

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        with pytest.raises(
            LocalGitError,
            match="Unable to determine the SHA for local ref",
        ):
            git_project.verify_upstream_unchanged(local_ref="HEAD", noop=False)


def test_verify_upstream_unchanged_with_custom_ref(
    tmp_path: Path, mock_repo: MagicMock
):
    """Test that verify_upstream_unchanged works with a custom ref like HEAD~1."""
    git_project = GitProject(directory=tmp_path)

    # Mock Repo as a context manager
    with patch("semantic_release.gitproject.Repo") as mock_repo_class:
        mock_repo_class.return_value.__enter__ = MagicMock(return_value=mock_repo)
        mock_repo_class.return_value.__exit__ = MagicMock(return_value=False)

        # Should not raise an exception
        git_project.verify_upstream_unchanged(local_ref="HEAD~1", noop=False)

    # Verify rev_parse was called with custom ref
    mock_repo.git.rev_parse.assert_called_once_with("HEAD~1")
