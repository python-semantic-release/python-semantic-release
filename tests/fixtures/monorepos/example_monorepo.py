from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

# NOTE: use backport with newer API
import tests.conftest
import tests.const
import tests.fixtures.example_project
import tests.util
from tests.const import (
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
)
from tests.util import copy_dir_tree, temporary_working_directory

if TYPE_CHECKING:
    from typing import Any, Protocol, Sequence

    from tests.conftest import (
        BuildRepoOrCopyCacheFn,
        GetMd5ForSetOfFilesFn,
    )
    from tests.fixtures.example_project import (
        UpdatePyprojectTomlFn,
        UpdateVersionPyFileFn,
    )
    from tests.fixtures.git_repo import RepoActions

    # class GetWheelFileFn(Protocol):
    #     def __call__(self, version_str: str) -> Path: ...

    class UpdatePkgPyprojectTomlFn(Protocol):
        def __call__(self, pkg_name: str, setting: str, value: Any) -> None: ...

    class UseCommonReleaseNotesTemplateFn(Protocol):
        def __call__(self) -> None: ...


@pytest.fixture(scope="session")
def deps_files_4_example_monorepo() -> list[Path]:
    return [
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
        Path(tests.fixtures.example_project.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_4_example_monorepo(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_example_monorepo: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_example_monorepo)


@pytest.fixture(scope="session")
def cached_example_monorepo(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    monorepo_pkg1_name: str,
    monorepo_pkg2_name: str,
    monorepo_pkg1_dir: str,
    monorepo_pkg2_dir: str,
    monorepo_pkg1_docs_dir: str,
    monorepo_pkg2_docs_dir: str,
    monorepo_pkg1_version_py_file: Path,
    monorepo_pkg2_version_py_file: Path,
    monorepo_pkg1_pyproject_toml_file: Path,
    monorepo_pkg2_pyproject_toml_file: Path,
    build_spec_hash_4_example_monorepo: str,
    update_version_py_file: UpdateVersionPyFileFn,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> Path:
    """
    Initializes the example monorepo project. DO NOT USE DIRECTLY

    Use the `init_example_monorepo` fixture instead.
    """

    def _build_project(cached_project_path: Path) -> Sequence[RepoActions]:
        # purposefully a relative path
        # example_dir = version_py_file.parent
        gitignore_contents = dedent(
            f"""
            *.pyc
            /{monorepo_pkg1_version_py_file}
            /{monorepo_pkg2_version_py_file}
            dist/
            """
        ).lstrip()
        init_py_contents = dedent(
            '''
            """An example package with a very informative docstring."""
            from ._version import __version__

            def hello_world() -> None:
                print("{pkg_name} Hello World")
            '''
        ).lstrip()
        doc_index_contents = dedent(
            """
            ==================
            {pkg_name} Documentation
            ==================
            """
        ).lstrip()

        with temporary_working_directory(cached_project_path):
            update_version_py_file(
                version=EXAMPLE_PROJECT_VERSION,
                version_file=monorepo_pkg1_version_py_file,
            )
            update_version_py_file(
                version=EXAMPLE_PROJECT_VERSION,
                version_file=monorepo_pkg2_version_py_file,
            )

        file_2_contents: list[tuple[str | Path, str]] = [
            (
                monorepo_pkg1_version_py_file.parent / "__init__.py",
                init_py_contents.format(pkg_name="Pkg 1:"),
            ),
            (
                monorepo_pkg2_version_py_file.parent / "__init__.py",
                init_py_contents.format(pkg_name="Pkg 2:"),
            ),
            (".gitignore", gitignore_contents),
            (monorepo_pkg1_pyproject_toml_file, EXAMPLE_PYPROJECT_TOML_CONTENT),
            (monorepo_pkg2_pyproject_toml_file, EXAMPLE_PYPROJECT_TOML_CONTENT),
            (
                Path(monorepo_pkg1_docs_dir, "index.rst"),
                doc_index_contents.format(pkg_name=monorepo_pkg1_name),
            ),
            (
                Path(monorepo_pkg2_docs_dir, "index.rst"),
                doc_index_contents.format(pkg_name=monorepo_pkg2_name),
            ),
        ]

        for file, contents in file_2_contents:
            abs_filepath = cached_project_path.joinpath(file).resolve()
            # make sure the parent directory exists
            abs_filepath.parent.mkdir(parents=True, exist_ok=True)
            # write file contents
            abs_filepath.write_text(contents)

        config_updates: list[tuple[str, Any, Path]] = [
            (
                "tool.poetry.name",
                "pkg-1",
                cached_project_path / monorepo_pkg1_pyproject_toml_file,
            ),
            (
                "tool.poetry.name",
                "pkg-2",
                cached_project_path / monorepo_pkg2_pyproject_toml_file,
            ),
            (
                "tool.semantic_release.version_variables",
                [
                    f"{monorepo_pkg1_version_py_file.relative_to(monorepo_pkg1_dir)}:__version__"
                ],
                cached_project_path / monorepo_pkg1_pyproject_toml_file,
            ),
            (
                "tool.semantic_release.version_variables",
                [
                    f"{monorepo_pkg2_version_py_file.relative_to(monorepo_pkg2_dir)}:__version__"
                ],
                cached_project_path / monorepo_pkg2_pyproject_toml_file,
            ),
        ]

        for setting, value, toml_file in config_updates:
            update_pyproject_toml(
                setting=setting,
                value=value,
                toml_file=toml_file,
            )

        # This is a special build, we don't expose the Repo Actions to the caller
        return []

    # End of _build_project()

    return build_repo_or_copy_cache(
        repo_name="example_monorepo",
        build_spec_hash=build_spec_hash_4_example_monorepo,
        build_repo_func=_build_project,
    )


@pytest.fixture
def init_example_monorepo(
    example_project_dir: tests.fixtures.example_project.ExProjectDir,
    cached_example_monorepo: Path,
    change_to_ex_proj_dir: None,
) -> None:
    """This fixture initializes the example project in the current test's project directory."""
    if not cached_example_monorepo.exists():
        raise RuntimeError(
            f"Unable to find cached project files for {EXAMPLE_PROJECT_NAME}"
        )

    # Copy the cached project files into the current test's project directory
    copy_dir_tree(cached_example_monorepo, example_project_dir)


@pytest.fixture
def monorepo_project_w_common_release_notes_template(
    init_example_monorepo: None,
    monorepo_use_common_release_notes_template: UseCommonReleaseNotesTemplateFn,
) -> None:
    monorepo_use_common_release_notes_template()


@pytest.fixture(scope="session")
def monorepo_pkg1_name() -> str:
    return "pkg1"


@pytest.fixture(scope="session")
def monorepo_pkg2_name() -> str:
    return "pkg2"


@pytest.fixture(scope="session")
def monorepo_pkg_docs_dir_pattern() -> str:
    return str(Path("docs", "source", "{package_name}"))


@pytest.fixture(scope="session")
def monorepo_pkg1_docs_dir(
    monorepo_pkg1_name: str,
    monorepo_pkg_docs_dir_pattern: str,
) -> str:
    return monorepo_pkg_docs_dir_pattern.format(package_name=monorepo_pkg1_name)


@pytest.fixture(scope="session")
def monorepo_pkg2_docs_dir(
    monorepo_pkg2_name: str,
    monorepo_pkg_docs_dir_pattern: str,
) -> str:
    return monorepo_pkg_docs_dir_pattern.format(package_name=monorepo_pkg2_name)


@pytest.fixture(scope="session")
def monorepo_pkg_dir_pattern() -> str:
    return str(Path("packages", "{package_name}"))


@pytest.fixture(scope="session")
def monorepo_pkg1_dir(
    monorepo_pkg1_name: str,
    monorepo_pkg_dir_pattern: str,
) -> str:
    return monorepo_pkg_dir_pattern.format(package_name=monorepo_pkg1_name)


@pytest.fixture(scope="session")
def monorepo_pkg2_dir(
    monorepo_pkg2_name: str,
    monorepo_pkg_dir_pattern: str,
) -> str:
    return monorepo_pkg_dir_pattern.format(package_name=monorepo_pkg2_name)


@pytest.fixture(scope="session")
def monorepo_pkg_version_py_file_pattern(monorepo_pkg_dir_pattern: str) -> str:
    return str(Path(monorepo_pkg_dir_pattern, "src", "{package_name}", "_version.py"))


@pytest.fixture(scope="session")
def monorepo_pkg1_version_py_file(
    monorepo_pkg1_name: str,
    monorepo_pkg_version_py_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_version_py_file_pattern.format(package_name=monorepo_pkg1_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg2_version_py_file(
    monorepo_pkg2_name: str,
    monorepo_pkg_version_py_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_version_py_file_pattern.format(package_name=monorepo_pkg2_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg_pyproject_toml_file_pattern(
    monorepo_pkg_dir_pattern: str,
    pyproject_toml_file: str,
) -> str:
    return str(Path(monorepo_pkg_dir_pattern, pyproject_toml_file))


@pytest.fixture(scope="session")
def monorepo_pkg1_pyproject_toml_file(
    monorepo_pkg1_name: str,
    monorepo_pkg_pyproject_toml_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_pyproject_toml_file_pattern.format(package_name=monorepo_pkg1_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg2_pyproject_toml_file(
    monorepo_pkg2_name: str,
    monorepo_pkg_pyproject_toml_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_pyproject_toml_file_pattern.format(package_name=monorepo_pkg2_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg_dist_dir_pattern(monorepo_pkg_dir_pattern: str) -> str:
    return str(Path(monorepo_pkg_dir_pattern, "dist"))


@pytest.fixture(scope="session")
def monorepo_pkg1_dist_dir(
    monorepo_pkg1_name: str,
    monorepo_pkg_dist_dir_pattern: str,
) -> Path:
    return Path(monorepo_pkg_dist_dir_pattern.format(package_name=monorepo_pkg1_name))


@pytest.fixture(scope="session")
def monorepo_pkg2_dist_dir(
    monorepo_pkg2_name: str,
    monorepo_pkg_dist_dir_pattern: str,
) -> Path:
    return Path(monorepo_pkg_dist_dir_pattern.format(package_name=monorepo_pkg2_name))


@pytest.fixture(scope="session")
def monorepo_pkg_changelog_md_file_pattern(monorepo_pkg_dir_pattern: str) -> str:
    return str(Path(monorepo_pkg_dir_pattern, "CHANGELOG.md"))


@pytest.fixture(scope="session")
def monorepo_pkg1_changelog_md_file(
    monorepo_pkg1_name: str,
    monorepo_pkg_changelog_md_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_changelog_md_file_pattern.format(package_name=monorepo_pkg1_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg2_changelog_md_file(
    monorepo_pkg2_name: str,
    monorepo_pkg_changelog_md_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_changelog_md_file_pattern.format(package_name=monorepo_pkg2_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg_changelog_rst_file_pattern(monorepo_pkg_dir_pattern: str) -> str:
    return str(Path(monorepo_pkg_dir_pattern, "CHANGELOG.rst"))


@pytest.fixture(scope="session")
def monorepo_pkg1_changelog_rst_file(
    monorepo_pkg1_name: str,
    monorepo_pkg_changelog_rst_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_changelog_rst_file_pattern.format(package_name=monorepo_pkg1_name)
    )


@pytest.fixture(scope="session")
def monorepo_pkg2_changelog_rst_file(
    monorepo_pkg2_name: str,
    monorepo_pkg_changelog_rst_file_pattern: str,
) -> Path:
    return Path(
        monorepo_pkg_changelog_rst_file_pattern.format(package_name=monorepo_pkg2_name)
    )


# @pytest.fixture(scope="session")
# def get_wheel_file(dist_dir: Path) -> GetWheelFileFn:
#     def _get_wheel_file(version_str: str) -> Path:
#         return dist_dir / f"{EXAMPLE_PROJECT_NAME}-{version_str}-py3-none-any.whl"

#     return _get_wheel_file


@pytest.fixture
def example_monorepo_pkg_dir_pattern(
    tmp_path: Path,
    monorepo_pkg_dir_pattern: Path,
) -> str:
    return str(tmp_path.resolve() / monorepo_pkg_dir_pattern)


@pytest.fixture
def example_monorepo_pkg1_dir(
    monorepo_pkg1_name: str,
    example_monorepo_pkg_dir_pattern: str,
) -> Path:
    return Path(
        example_monorepo_pkg_dir_pattern.format(package_name=monorepo_pkg1_name)
    )


@pytest.fixture
def example_monorepo_pkg2_dir(
    monorepo_pkg2_name: str,
    example_monorepo_pkg_dir_pattern: str,
) -> Path:
    return Path(
        example_monorepo_pkg_dir_pattern.format(package_name=monorepo_pkg2_name)
    )


@pytest.fixture
def monorepo_use_common_release_notes_template(
    example_project_template_dir: Path,
    changelog_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    monorepo_pkg1_pyproject_toml_file: Path,
    monorepo_pkg2_pyproject_toml_file: Path,
) -> UseCommonReleaseNotesTemplateFn:
    config_setting_template_dir = "tool.semantic_release.changelog.template_dir"

    def _use_release_notes_template() -> None:
        update_pyproject_toml(
            setting=config_setting_template_dir,
            value=str(
                Path(
                    *(
                        "../"
                        for _ in list(Path(monorepo_pkg1_pyproject_toml_file).parents)[
                            :-1
                        ]
                    ),
                    changelog_template_dir,
                )
            ),
            toml_file=monorepo_pkg1_pyproject_toml_file,
        )

        update_pyproject_toml(
            setting=config_setting_template_dir,
            value=str(
                Path(
                    *(
                        "../"
                        for _ in list(Path(monorepo_pkg2_pyproject_toml_file).parents)[
                            :-1
                        ]
                    ),
                    changelog_template_dir,
                )
            ),
            toml_file=monorepo_pkg2_pyproject_toml_file,
        )

        example_project_template_dir.mkdir(parents=True, exist_ok=True)
        release_notes_j2 = example_project_template_dir / ".release_notes.md.j2"
        release_notes_j2.write_text(EXAMPLE_RELEASE_NOTES_TEMPLATE)

    return _use_release_notes_template


# @pytest.fixture
# def example_pyproject_toml(
#     example_project_dir: ExProjectDir,
#     pyproject_toml_file: Path,
# ) -> Path:
#     return example_project_dir / pyproject_toml_file


# @pytest.fixture
# def example_dist_dir(
#     example_project_dir: ExProjectDir,
#     dist_dir: Path,
# ) -> Path:
#     return example_project_dir / dist_dir


# @pytest.fixture
# def example_project_wheel_file(
#     example_dist_dir: Path,
#     get_wheel_file: GetWheelFileFn,
# ) -> Path:
#     return example_dist_dir / get_wheel_file(EXAMPLE_PROJECT_VERSION)


# Note this is just the path and the content may change
# @pytest.fixture
# def example_changelog_md(
#     example_project_dir: ExProjectDir,
#     changelog_md_file: Path,
# ) -> Path:
#     return example_project_dir / changelog_md_file


# Note this is just the path and the content may change
# @pytest.fixture
# def example_changelog_rst(
#     example_project_dir: ExProjectDir,
#     changelog_rst_file: Path,
# ) -> Path:
#     return example_project_dir / changelog_rst_file


# @pytest.fixture
# def example_project_template_dir(
#     example_project_dir: ExProjectDir,
#     changelog_template_dir: Path,
# ) -> Path:
#     return example_project_dir / changelog_template_dir


@pytest.fixture(scope="session")
def update_pkg_pyproject_toml(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    monorepo_pkg_pyproject_toml_file_pattern: str,
) -> UpdatePkgPyprojectTomlFn:
    """Update the pyproject.toml file with the given content."""

    def _update_pyproject_toml(pkg_name: str, setting: str, value: Any) -> None:
        toml_file = Path(
            monorepo_pkg_pyproject_toml_file_pattern.format(package_name=pkg_name)
        ).resolve()

        if not toml_file.exists():
            raise FileNotFoundError(
                f"pyproject.toml file for package {pkg_name} not found at {toml_file}"
            )

        update_pyproject_toml(
            setting=setting,
            value=value,
            toml_file=toml_file,
        )

    return _update_pyproject_toml
