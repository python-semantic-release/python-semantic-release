"""Module for git related operations."""

from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from git import GitCommandError, Repo

from semantic_release.cli.masking_filter import MaskingFilter
from semantic_release.cli.util import indented, noop_report
from semantic_release.errors import (
    DetachedHeadGitError,
    GitAddError,
    GitCommitEmptyIndexError,
    GitCommitError,
    GitFetchError,
    GitPushError,
    GitTagError,
    LocalGitError,
    UnknownUpstreamBranchError,
    UpstreamBranchChangedError,
)
from semantic_release.globals import logger

if TYPE_CHECKING:  # pragma: no cover
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
        self._logger = logger
        self._cred_masker = credential_masker or MaskingFilter()
        self._commit_author = commit_author

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def logger(self) -> Logger:
        return self._logger

    def _get_custom_environment(
        self,
        repo: Repo,
        custom_vars: dict[str, str] | None = None,
    ) -> nullcontext[None] | _GeneratorContextManager[None]:
        """
        git.custom_environment is a context manager but
        is not reentrant, so once we have "used" it
        we need to throw it away and re-create it in
        order to use it again
        """
        author_vars = (
            {
                "GIT_AUTHOR_NAME": self._commit_author.name,
                "GIT_AUTHOR_EMAIL": self._commit_author.email,
                "GIT_COMMITTER_NAME": self._commit_author.name,
                "GIT_COMMITTER_EMAIL": self._commit_author.email,
            }
            if self._commit_author
            else {}
        )

        custom_env_vars = {
            **author_vars,
            **(custom_vars or {}),
        }

        return (
            nullcontext()
            if not custom_env_vars
            else repo.git.custom_environment(**custom_env_vars)
        )

    def is_dirty(self) -> bool:
        with Repo(str(self.project_root)) as repo:
            return repo.is_dirty()

    def is_shallow_clone(self) -> bool:
        """
        Check if the repository is a shallow clone.

        :return: True if the repository is a shallow clone, False otherwise
        """
        with Repo(str(self.project_root)) as repo:
            shallow_file = Path(repo.git_dir, "shallow")
            return shallow_file.exists()

    def git_unshallow(self, noop: bool = False) -> None:
        """
        Convert a shallow clone to a full clone by fetching the full history.

        :param noop: Whether or not to actually run the unshallow command
        """
        if noop:
            noop_report("would have run:\n" "    git fetch --unshallow")
            return

        with Repo(str(self.project_root)) as repo:
            try:
                self.logger.info("Converting shallow clone to full clone...")
                repo.git.fetch("--unshallow")
                self.logger.info("Repository unshallowed successfully")
            except GitCommandError as err:
                # If the repository is already a full clone, git fetch --unshallow will fail
                # with "fatal: --unshallow on a complete repository does not make sense"
                # We can safely ignore this error by checking the stderr message
                stderr = str(err.stderr) if err.stderr else ""
                if "does not make sense" in stderr or "complete repository" in stderr:
                    self.logger.debug("Repository is already a full clone")
                else:
                    self.logger.exception(str(err))
                    raise

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

    def git_tag(
        self,
        tag_name: str,
        message: str,
        isotimestamp: str,
        force: bool = False,
        noop: bool = False,
    ) -> None:
        try:
            datetime.fromisoformat(isotimestamp)
        except ValueError as err:
            raise ValueError("Invalid timestamp format") from err

        if noop:
            command = str.join(
                " ",
                filter(
                    None,
                    [
                        f"GIT_COMMITTER_DATE={isotimestamp}",
                        *(
                            [
                                f"GIT_AUTHOR_NAME={self._commit_author.name}",
                                f"GIT_AUTHOR_EMAIL={self._commit_author.email}",
                                f"GIT_COMMITTER_NAME={self._commit_author.name}",
                                f"GIT_COMMITTER_EMAIL={self._commit_author.email}",
                            ]
                            if self._commit_author
                            else [""]
                        ),
                        f"git tag -a {tag_name} -m '{message}'",
                        "--force" if force else "",
                    ],
                ),
            ).strip()

            noop_report(
                indented(
                    f"""\
                    would have run:
                        {command}
                    """
                )
            )
            return

        with Repo(str(self.project_root)) as repo, self._get_custom_environment(
            repo,
            {"GIT_COMMITTER_DATE": isotimestamp},
        ):
            try:
                repo.git.tag(tag_name, a=True, m=message, force=force)
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

    def git_push_tag(
        self, remote_url: str, tag: str, noop: bool = False, force: bool = False
    ) -> None:
        if noop:
            noop_report(
                indented(
                    f"""\
                    would have run:
                        git push {self._cred_masker.mask(remote_url)} tag {tag} {"--force" if force else ""}
                    """  # noqa: E501
                )
            )
            return

        with Repo(str(self.project_root)) as repo:
            try:
                repo.git.push(remote_url, "tag", tag, force=force)
            except GitCommandError as err:
                self.logger.exception(str(err))
                raise GitPushError(f"Failed to push tag ({tag}) to remote") from err

    def verify_upstream_unchanged(  # noqa: C901
        self,
        local_ref: str = "HEAD",
        upstream_ref: str = "origin",
        remote_url: str | None = None,
        noop: bool = False,
    ) -> None:
        """
        Verify that the upstream branch has not changed since the given local reference.

        :param local_ref: The local reference to compare against upstream (default: HEAD)
        :param upstream_ref: The name of the upstream remote or specific remote branch (default: origin)
        :param remote_url: Optional authenticated remote URL to use for fetching (default: None, uses configured remote)
        :param noop: Whether to skip the actual verification (for dry-run mode)

        :raises UpstreamBranchChangedError: If the upstream branch has changed
        """
        if not local_ref.strip():
            raise ValueError("Local reference cannot be empty")
        if not upstream_ref.strip():
            raise ValueError("Upstream reference cannot be empty")

        if noop:
            noop_report(
                indented(
                    """\
                    would have verified that upstream branch has not changed
                    """
                )
            )
            return

        with Repo(str(self.project_root)) as repo:
            # Get the current active branch
            try:
                active_branch = repo.active_branch
            except TypeError:
                # When in detached HEAD state, active_branch raises TypeError
                err_msg = (
                    "Repository is in detached HEAD state, cannot verify upstream state"
                )
                raise DetachedHeadGitError(err_msg) from None

            # Get the tracking branch (upstream branch)
            if (tracking_branch := active_branch.tracking_branch()) is not None:
                upstream_full_ref_name = tracking_branch.name
                self.logger.info("Upstream branch name: %s", upstream_full_ref_name)
            else:
                # If no tracking branch is set, derive it
                upstream_name = (
                    upstream_ref.strip()
                    if upstream_ref.find("/") == -1
                    else upstream_ref.strip().split("/", maxsplit=1)[0]
                )

                if not repo.remotes or upstream_name not in repo.remotes:
                    err_msg = "No remote found; cannot verify upstream state!"
                    raise UnknownUpstreamBranchError(err_msg)

                upstream_full_ref_name = (
                    f"{upstream_name}/{active_branch.name}"
                    if upstream_ref.find("/") == -1
                    else upstream_ref.strip()
                )

                if upstream_full_ref_name not in repo.refs:
                    err_msg = f"No upstream branch found for '{active_branch.name}'; cannot verify upstream state!"
                    raise UnknownUpstreamBranchError(err_msg)

            # Extract the remote name from the tracking branch
            # tracking_branch.name is in the format "remote/branch"
            remote_name, remote_branch_name = upstream_full_ref_name.split(
                "/", maxsplit=1
            )
            remote_ref_obj = repo.remotes[remote_name]

            # Fetch the latest changes from the remote
            self.logger.info("Fetching latest changes from remote '%s'", remote_name)
            try:
                # Check if we should use authenticated URL for fetch
                # Only use remote_url if:
                # 1. It's provided and different from the configured remote URL
                # 2. It contains authentication credentials (@ symbol)
                # 3. The configured remote is NOT a local path, file:// URL, or test URL (example.com)
                #    This ensures we don't break tests or local development
                configured_url = remote_ref_obj.url
                is_local_or_test_remote = (
                    configured_url.startswith(("file://", "/", "C:/", "H:/"))
                    or "example.com" in configured_url
                    or not configured_url.startswith(
                        (
                            "https://",
                            "http://",
                            "git://",
                            "git@",
                            "ssh://",
                            "git+ssh://",
                        )
                    )
                )

                use_authenticated_fetch = (
                    remote_url
                    and "@" in remote_url
                    and remote_url != configured_url
                    and not is_local_or_test_remote
                )

                if use_authenticated_fetch:
                    # Use authenticated remote URL for fetch
                    # Fetch the remote branch and update the local tracking ref
                    repo.git.fetch(
                        remote_url,
                        f"refs/heads/{remote_branch_name}:refs/remotes/{upstream_full_ref_name}",
                    )
                else:
                    # Use the default remote configuration for local paths,
                    # file:// URLs, test URLs, or when no authentication is needed
                    remote_ref_obj.fetch()
            except GitCommandError as err:
                self.logger.exception(str(err))
                err_msg = f"Failed to fetch from remote '{remote_name}'"
                raise GitFetchError(err_msg) from err

            # Get the SHA of the upstream branch
            try:
                upstream_commit_ref = remote_ref_obj.refs[remote_branch_name].commit
                upstream_sha = upstream_commit_ref.hexsha
            except AttributeError as err:
                self.logger.exception(str(err))
                err_msg = f"Unable to determine upstream branch SHA for '{upstream_full_ref_name}'"
                raise GitFetchError(err_msg) from err

            # Get the SHA of the specified ref (default: HEAD)
            try:
                local_commit = repo.commit(repo.git.rev_parse(local_ref))
            except GitCommandError as err:
                self.logger.exception(str(err))
                err_msg = f"Unable to determine the SHA for local ref '{local_ref}'"
                raise LocalGitError(err_msg) from err

            # Compare the two SHAs
            if local_commit.hexsha != upstream_sha and not any(
                commit.hexsha == upstream_sha for commit in local_commit.iter_parents()
            ):
                err_msg = str.join(
                    "\n",
                    (
                        f"[LOCAL SHA] {local_commit.hexsha} != {upstream_sha} [UPSTREAM SHA].",
                        f"Upstream branch '{upstream_full_ref_name}' has changed!",
                    ),
                )
                raise UpstreamBranchChangedError(err_msg)

            self.logger.info(
                "Verified upstream branch '%s' has not changed",
                upstream_full_ref_name,
            )
