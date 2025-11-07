from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING

import pytest
from git import Repo

import tests.conftest
import tests.const
import tests.fixtures.git_repo
import tests.util
from tests.const import (
    DEFAULT_BRANCH_NAME,
    EXAMPLE_HVCS_DOMAIN,
    EXAMPLE_PROJECT_NAME,
)
from tests.util import copy_dir_tree

if TYPE_CHECKING:
    from typing import Protocol, Sequence

    from git import Actor

    from semantic_release.hvcs import HvcsBase

    from tests.conftest import (
        BuildRepoOrCopyCacheFn,
        GetMd5ForSetOfFilesFn,
        RepoActions,
    )
    from tests.fixtures.git_repo import (
        BuildRepoFn,
        CommitConvention,
        TomlSerializableTypes,
    )

    class BuildMonorepoFn(Protocol):
        def __call__(self, dest_dir: Path | str) -> Path: ...


@pytest.fixture(scope="session")
def deps_files_4_example_git_monorepo(
    deps_files_4_example_monorepo: list[Path],
) -> list[Path]:
    return [
        *deps_files_4_example_monorepo,
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
        Path(tests.fixtures.git_repo.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_4_example_git_monorepo(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_example_git_monorepo: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_example_git_monorepo)


@pytest.fixture(scope="session")
def cached_example_git_monorepo(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    build_spec_hash_4_example_git_monorepo: str,
    cached_example_monorepo: Path,
    example_git_https_url: str,
    commit_author: Actor,
) -> Path:
    """
    Initializes an example monorepo project with git. DO NOT USE DIRECTLY.

    Use a `repo_*` fixture instead. This creates a default
    base repository, all settings can be changed later through from the
    example_project_git_repo fixture's return object and manual adjustment.
    """

    def _build_repo(cached_repo_path: Path) -> Sequence[RepoActions]:
        if not cached_example_monorepo.exists():
            raise RuntimeError("Unable to find cached monorepo files")

        # make a copy of the example monorepo as a base
        copy_dir_tree(cached_example_monorepo, cached_repo_path)

        # initialize git repo (open and close)
        # NOTE: We don't want to hold the repo object open for the entire test session,
        # the implementation on Windows holds some file descriptors open until close is called.
        with Repo.init(cached_repo_path) as repo:
            rmtree(str(Path(repo.git_dir, "hooks")))

            # set up remote origin (including a refs directory)
            git_origin_dir = Path(repo.common_dir, "refs", "remotes", "origin")
            repo.create_remote(name=git_origin_dir.name, url=example_git_https_url)
            git_origin_dir.mkdir(parents=True, exist_ok=True)

            # Without this the global config may set it to "master", we want consistency
            repo.git.branch("-M", DEFAULT_BRANCH_NAME)

            with repo.config_writer("repository") as config:
                config.set_value("user", "name", commit_author.name)
                config.set_value("user", "email", commit_author.email)
                config.set_value("commit", "gpgsign", False)
                config.set_value("tag", "gpgsign", False)

                # set up a remote tracking branch for the default branch
                config.set_value(f'branch "{DEFAULT_BRANCH_NAME}"', "remote", "origin")
                config.set_value(
                    f'branch "{DEFAULT_BRANCH_NAME}"',
                    "merge",
                    f"refs/heads/{DEFAULT_BRANCH_NAME}",
                )

            # make sure all base files are in index to enable initial commit
            repo.index.add(("*", ".gitignore"))

        # This is a special build, we don't expose the Repo Actions to the caller
        return []

    # End of _build_repo()

    return build_repo_or_copy_cache(
        repo_name=cached_example_git_monorepo.__name__.split("_", maxsplit=1)[1],
        build_spec_hash=build_spec_hash_4_example_git_monorepo,
        build_repo_func=_build_repo,
    )


@pytest.fixture(scope="session")
def file_in_pkg_pattern(file_in_repo: str, monorepo_pkg_dir_pattern: str) -> str:
    return str(Path(monorepo_pkg_dir_pattern) / file_in_repo)


@pytest.fixture(scope="session")
def file_in_monorepo_pkg1(
    monorepo_pkg1_name: str,
    file_in_pkg_pattern: str,
) -> Path:
    return Path(file_in_pkg_pattern.format(pkg_name=monorepo_pkg1_name))


@pytest.fixture(scope="session")
def file_in_monorepo_pkg2(
    monorepo_pkg2_name: str,
    file_in_pkg_pattern: str,
) -> Path:
    return Path(file_in_pkg_pattern.format(pkg_name=monorepo_pkg2_name))


@pytest.fixture(scope="session")
def build_base_monorepo(  # noqa: C901
    cached_example_git_monorepo: Path,
) -> BuildMonorepoFn:
    """
    This fixture is intended to simplify repo scenario building by initially
    creating the repo but also configuring semantic_release in the pyproject.toml
    for when the test executes semantic_release. It returns a function so that
    derivative fixtures can call this fixture with individual parameters.
    """

    def _build_configured_base_monorepo(dest_dir: Path | str) -> Path:
        if not cached_example_git_monorepo.exists():
            raise RuntimeError("Unable to find cached git project files!")

        # Copy the cached git project the dest directory
        copy_dir_tree(cached_example_git_monorepo, dest_dir)

        return Path(dest_dir)

    return _build_configured_base_monorepo


@pytest.fixture(scope="session")
def configure_monorepo_package(  # noqa: C901
    configure_base_repo: BuildRepoFn,
) -> BuildRepoFn:
    """
    This fixture is intended to simplify repo scenario building by initially
    creating the repo but also configuring semantic_release in the pyproject.toml
    for when the test executes semantic_release. It returns a function so that
    derivative fixtures can call this fixture with individual parameters.
    """

    def _configure(  # noqa: C901
        dest_dir: Path | str,
        commit_type: CommitConvention = "conventional",
        hvcs_client_name: str = "github",
        hvcs_domain: str = EXAMPLE_HVCS_DOMAIN,
        tag_format_str: str | None = None,
        extra_configs: dict[str, TomlSerializableTypes] | None = None,
        mask_initial_release: bool = True,  # Default as of v10
        package_name: str = EXAMPLE_PROJECT_NAME,
        monorepo: bool = True,
    ) -> tuple[Path, HvcsBase]:
        if not monorepo:
            raise ValueError("This fixture is only for monorepo packages!")

        if not Path(dest_dir).exists():
            raise RuntimeError(f"Destination directory {dest_dir} does not exist!")

        return configure_base_repo(
            dest_dir=dest_dir,
            commit_type=commit_type,
            hvcs_client_name=hvcs_client_name,
            hvcs_domain=hvcs_domain,
            tag_format_str=tag_format_str,
            extra_configs=extra_configs,
            mask_initial_release=mask_initial_release,
            package_name=package_name,
            monorepo=monorepo,
        )

    return _configure
