from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Generator

import pytest
import tomlkit

from semantic_release.commit_parser import (
    AngularCommitParser,
    EmojiCommitParser,
    ScipyCommitParser,
    TagCommitParser,
)
from semantic_release.hvcs import Gitea, Github, Gitlab

from tests.const import (
    EXAMPLE_CHANGELOG_MD_CONTENT,
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_SETUP_CFG_CONTENT,
    EXAMPLE_SETUP_PY_CONTENT,
)

if TYPE_CHECKING:
    from typing import Any, Protocol

    from semantic_release.commit_parser import CommitParser
    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn

    ExProjectDir = Path

    class UpdatePyprojectTomlFn(Protocol):
        def __call__(self, setting: str, value: Any) -> None:
            ...

    class UseHvcsFn(Protocol):
        def __call__(self) -> type[HvcsBase]:
            ...

    class UseParserFn(Protocol):
        def __call__(self) -> type[CommitParser]:
            ...


@pytest.fixture(scope="session")
def pyproject_toml_file() -> Path:
    return Path("pyproject.toml")


@pytest.fixture(scope="session")
def setup_cfg_file() -> Path:
    return Path("setup.cfg")


@pytest.fixture(scope="session")
def setup_py_file() -> Path:
    return Path("setup.py")


@pytest.fixture(scope="session")
def changelog_md_file() -> Path:
    return Path("CHANGELOG.md")


@pytest.fixture(scope="session")
def changelog_template_dir() -> Path:
    return Path("templates")


@pytest.fixture
def example_project_dir(tmp_path: Path) -> ExProjectDir:
    return tmp_path.resolve()



@pytest.fixture
def change_to_ex_proj_dir(example_project_dir: ExProjectDir) -> Generator[None, None, None]:
    cwd = os.getcwd()
    tgt_dir = str(example_project_dir.resolve())
    if cwd == tgt_dir:
        return

    os.chdir(tgt_dir)
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture(scope="session")
def cached_example_project(
    pyproject_toml_file: Path,
    setup_cfg_file: Path,
    setup_py_file: Path,
    changelog_md_file: Path,
    cached_files_dir: Path,
    changelog_template_dir: Path,
    teardown_cached_dir: TeardownCachedDirFn,
) -> Path:
    """
    Initializes the example project. DO NOT USE DIRECTLY

    Use the `init_example_project` fixture instead.
    """
    cached_project_path = (cached_files_dir / "example_project").resolve()
    # purposefully a relative path
    example_dir = Path("src", EXAMPLE_PROJECT_NAME)
    version_py = example_dir / "_version.py"
    gitignore_contents = dedent(
        f"""
        *.pyc
        /src/**/{version_py.name}
        """
    ).lstrip()
    init_py_contents = dedent(
        '''
        """
        An example package with a very informative docstring
        """
        from ._version import __version__


        def hello_world() -> None:
            print("Hello World")
        '''
    ).lstrip()
    version_py_contents = dedent(
        f"""
        __version__ = "{EXAMPLE_PROJECT_VERSION}"
        """
    ).lstrip()

    for file, contents in [
        (example_dir / "__init__.py", init_py_contents),
        (version_py, version_py_contents),
        (".gitignore", gitignore_contents),
        (pyproject_toml_file, EXAMPLE_PYPROJECT_TOML_CONTENT),
        (setup_cfg_file, EXAMPLE_SETUP_CFG_CONTENT),
        (setup_py_file, EXAMPLE_SETUP_PY_CONTENT),
        (changelog_md_file, EXAMPLE_CHANGELOG_MD_CONTENT),
    ]:
        abs_filepath = cached_project_path.joinpath(file).resolve()
        # make sure the parent directory exists
        abs_filepath.parent.mkdir(parents=True, exist_ok=True)
        # write file contents
        abs_filepath.write_text(contents)

    # create the changelog template directory
    cached_project_path.joinpath(changelog_template_dir).mkdir(parents=True, exist_ok=True)

    # trigger automatic cleanup of cache directory during teardown
    return teardown_cached_dir(cached_project_path)


@pytest.fixture
def init_example_project(
    example_project_dir: ExProjectDir,
    cached_example_project: Path,
    change_to_ex_proj_dir: None,
) -> None:
    """This fixture initializes the example project in the current test's project directory."""
    if not cached_example_project.exists():
        raise RuntimeError(
            f"Unable to find cached project files for {EXAMPLE_PROJECT_NAME}"
        )

    # Copy the cached project files into the current test's project directory
    if sys.version_info[:2] == (3, 7):
        # For 3.7 compatibility, destination can't exist, and dirs_exist_ok isn't available
        # since destination had to be removed, handle changing directories to prevent error
        os.chdir(str(example_project_dir.parent))
        shutil.rmtree(str(example_project_dir), ignore_errors=True)
        shutil.copytree(
            src=str(cached_example_project),
            dst=str(example_project_dir),
        )
        os.chdir(str(example_project_dir))
        return

    shutil.copytree(
        src=str(cached_example_project),
        dst=str(example_project_dir),
        dirs_exist_ok=True,
    )


@pytest.fixture
def example_project_with_release_notes_template(
    init_example_project: None,
    example_project_dir: Path,
) -> Path:
    template_dir = example_project_dir / "templates"
    release_notes_j2 = template_dir / ".release_notes.md.j2"
    release_notes_j2.write_text(EXAMPLE_RELEASE_NOTES_TEMPLATE)
    return example_project_dir


@pytest.fixture
def example_pyproject_toml(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / "pyproject.toml"


@pytest.fixture
def example_setup_cfg(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / "setup.cfg"


@pytest.fixture
def example_setup_py(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / "setup.py"


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_md(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / "CHANGELOG.md"


@pytest.fixture
def example_project_template_dir(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / "templates"


@pytest.fixture
def update_pyproject_toml(example_pyproject_toml: Path) -> UpdatePyprojectTomlFn:
    """Update the pyproject.toml file with the given content."""

    def _update_pyproject_toml(setting: str, value: Any) -> None:
        with open(example_pyproject_toml) as rfd:
            pyproject_toml = tomlkit.load(rfd)

        new_setting = {}
        parts = setting.split(".")
        new_setting_key = parts.pop(-1)
        new_setting[new_setting_key] = value

        pointer = pyproject_toml
        for part in parts:
            if pointer.get(part, None) is None:
                pointer.add(part, tomlkit.table())
            pointer = pointer.get(part, {})
        pointer.update(new_setting)

        with open(example_pyproject_toml, "w") as wfd:
            tomlkit.dump(pyproject_toml, wfd)

    return _update_pyproject_toml


@pytest.fixture
def use_angular_parser(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseParserFn:
    """Modify the configuration file to use the Angular parser."""

    def _use_angular_parser() -> type[CommitParser]:
        update_pyproject_toml("tool.semantic_release.commit_parser", "angular")
        return AngularCommitParser

    return _use_angular_parser


@pytest.fixture
def use_emoji_parser(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseParserFn:
    """Modify the configuration file to use the Emoji parser."""

    def _use_emoji_parser() -> type[CommitParser]:
        update_pyproject_toml("tool.semantic_release.commit_parser", "emoji")
        return EmojiCommitParser

    return _use_emoji_parser


@pytest.fixture
def use_scipy_parser(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseParserFn:
    """Modify the configuration file to use the Scipy parser."""

    def _use_scipy_parser() -> type[CommitParser]:
        update_pyproject_toml("tool.semantic_release.commit_parser", "scipy")
        return ScipyCommitParser

    return _use_scipy_parser


@pytest.fixture
def use_tag_parser(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseParserFn:
    """Modify the configuration file to use the Tag parser."""

    def _use_tag_parser() -> type[CommitParser]:
        update_pyproject_toml("tool.semantic_release.commit_parser", "tag")
        return TagCommitParser

    return _use_tag_parser


@pytest.fixture
def use_github_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use GitHub as the HVCS."""

    def _use_github_hvcs() -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "github")
        return Github

    return _use_github_hvcs


@pytest.fixture
def use_gitlab_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use GitLab as the HVCS."""

    def _use_gitlab_hvcs() -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "gitlab")
        return Gitlab

    return _use_gitlab_hvcs


@pytest.fixture
def use_gitea_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use Gitea as the HVCS."""

    def _use_gitea_hvcs() -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "gitea")
        return Gitea

    return _use_gitea_hvcs
