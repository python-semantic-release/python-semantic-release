"""Module for git related operations."""

from __future__ import annotations

from contextlib import nullcontext
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from git import GitCommandError, Repo

from semantic_release.cli.masking_filter import MaskingFilter
from semantic_release.cli.util import indented, noop_report
from semantic_release.errors import (
    GitAddError,
    GitCommitEmptyIndexError,
    GitCommitError,
    GitPushError,
    GitTagError,
)

if TYPE_CHECKING:
    from contextlib import _GeneratorContextManager
    from logging import Logger
    from typing import Sequence

    from git import Actor


class GitProject:
    def __init__(
        self,
        directory: Path | str = ".",
        commit_author: Actor | None = None,
        credential_masker: MaskingFilter | None = None,
    ) -> None:
        self._project_root = Path(directory).resolve()
        self._logger = getLogger(__name__)
        self._cred_masker = credential_masker or MaskingFilter()
        self._commit_author = commit_author

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def logger(self) -> Logger:
        return self._logger

    def _get_custom_environment(
        self, repo: Repo
    ) -> nullcontext[None] | _GeneratorContextManager[None]:
        """
        git.custom_environment is a context manager but
        is not reentrant, so once we have "used" it
        we need to throw it away and re-create it in
        order to use it again
        """
        return (
            nullcontext()
            if not self._commit_author
            else repo.git.custom_environment(
                GIT_AUTHOR_NAME=self._commit_author.name,
                GIT_AUTHOR_EMAIL=self._commit_author.email,
                GIT_COMMITTER_NAME=self._commit_author.name,
                GIT_COMMITTER_EMAIL=self._commit_author.email,
            )
        )

    def is_dirty(self) -> bool:
        with Repo(str(self.project_root)) as repo:
            return repo.is_dirty()

    def git_add(
        self,
        paths: Sequence[Path | str],
        force: bool = False,
        strict: bool = False,
        noop: bool = False,
    ) -> None:
        if noop:
            noop_report(
                indented(
                    f"""\
                    would have run:
                        git add {str.join(" ", [str(Path(p)) for p in paths])}
                    """
                )
            )
            return

        git_args = dict(
            filter(
                lambda k_v: k_v[1],  # if truthy
                {
                    "force": force,
                }.items(),
            )
        )

        with Repo(str(self.project_root)) as repo:
            # TODO: in future this loop should be 1 line:
            # repo.index.add(all_paths_to_add, force=False)  # noqa: ERA001
            # but since 'force' is deliberately ineffective (as in docstring) in gitpython 3.1.18
            # we have to do manually add each filepath, and catch the exception if it is an ignored file
            for updated_path in paths:
                try:
                    repo.git.add(str(Path(updated_path)), **git_args)
                except GitCommandError as err:  # noqa: PERF203, acceptable performance loss
                    err_msg = f"Failed to add path ({updated_path}) to index"
                    if strict:
                        self.logger.exception(str(err))
                        raise GitAddError(err_msg) from err
                    self.logger.warning(err_msg)

    def git_commit(
        self,
        message: str,
        date: int | None = None,
        commit_all: bool = False,
        no_verify: bool = False,
        noop: bool = False,
    ) -> None:
        git_args = dict(
            filter(
                lambda k_v: k_v[1],  # if truthy
                {
                    "a": commit_all,
                    "m": message,
                    "date": date,
                    "no_verify": no_verify,
                }.items(),
            )
        )

        if noop:
            command = (
                f"""\
                GIT_AUTHOR_NAME={self._commit_author.name} \\
                GIT_AUTHOR_EMAIL={self._commit_author.email} \\
                GIT_COMMITTER_NAME={self._commit_author.name} \\
                GIT_COMMITTER_EMAIL={self._commit_author.email} \\
                """
                if self._commit_author
                else ""
            )

            # Indents the newlines so that terminal formatting is happy - note the
            # git commit line of the output is 24 spaces indented too
            # Only this message needs such special handling because of the newlines
            # that might be in a commit message between the subject and body
            indented_commit_message = message.replace("\n\n", "\n\n" + " " * 24)

            command += f"git commit -m '{indented_commit_message}'"
            command += "--all" if commit_all else ""
            command += "--no-verify" if no_verify else ""

            noop_report(
                indented(
                    f"""\
                    would have run:
                        {command}
                    """
                )
            )
            return

        with Repo(str(self.project_root)) as repo:
            has_index_changes = bool(repo.index.diff("HEAD"))
            has_working_changes = self.is_dirty()
            will_commit_files = has_index_changes or (
                has_working_changes and commit_all
            )

            if not will_commit_files:
                raise GitCommitEmptyIndexError("No changes to commit!")

            with self._get_custom_environment(repo):
                try:
                    repo.git.commit(**git_args)
                except GitCommandError as err:
                    self.logger.exception(str(err))
                    raise GitCommitError("Failed to commit changes") from err

    def git_tag(self, tag_name: str, message: str, noop: bool = False) -> None:
        if noop:
            command = (
                f"""\
                GIT_AUTHOR_NAME={self._commit_author.name} \\
                GIT_AUTHOR_EMAIL={self._commit_author.email} \\
                GIT_COMMITTER_NAME={self._commit_author.name} \\
                GIT_COMMITTER_EMAIL={self._commit_author.email} \\
                """
                if self._commit_author
                else ""
            )
            command += f"git tag -a {tag_name} -m '{message}'"

            noop_report(
                indented(
                    f"""\
                    would have run:
                        {command}
                    """
                )
            )
            return

        with Repo(str(self.project_root)) as repo, self._get_custom_environment(repo):
            try:
                repo.git.tag("-a", tag_name, m=message)
            except GitCommandError as err:
                self.logger.exception(str(err))
                raise GitTagError(f"Failed to create tag ({tag_name})") from err

    def git_push_branch(self, remote_url: str, branch: str, noop: bool = False) -> None:
        if noop:
            noop_report(
                indented(
                    f"""\
                    would have run:
                        git push {self._cred_masker.mask(remote_url)} {branch}
                    """
                )
            )
            return

        with Repo(str(self.project_root)) as repo:
            try:
                repo.git.push(remote_url, branch)
            except GitCommandError as err:
                self.logger.exception(str(err))
                raise GitPushError(
                    f"Failed to push branch ({branch}) to remote"
                ) from err

    def git_push_tag(self, remote_url: str, tag: str, noop: bool = False) -> None:
        if noop:
            noop_report(
                indented(
                    f"""\
                    would have run:
                        git push {self._cred_masker.mask(remote_url)} tag {tag}
                    """  # noqa: E501
                )
            )
            return

        with Repo(str(self.project_root)) as repo:
            try:
                repo.git.push(remote_url, "tag", tag)
            except GitCommandError as err:
                self.logger.exception(str(err))
                raise GitPushError(f"Failed to push tag ({tag}) to remote") from err
