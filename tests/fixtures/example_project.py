from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Generator

import pytest
import tomlkit

import semantic_release
from semantic_release.commit_parser import (
    AngularCommitParser,
    EmojiCommitParser,
    ScipyCommitParser,
)
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab

from tests.const import (
    EXAMPLE_CHANGELOG_MD_CONTENT,
    EXAMPLE_CHANGELOG_RST_CONTENT,
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_SETUP_CFG_CONTENT,
    EXAMPLE_SETUP_PY_CONTENT,
)
from tests.util import copy_dir_tree

if TYPE_CHECKING:
    from typing import Any, Protocol

    from semantic_release.commit_parser import CommitParser
    from semantic_release.hvcs import HvcsBase

    from tests.conftest import TeardownCachedDirFn

    ExProjectDir = Path

    class GetWheelFileFn(Protocol):
        def __call__(self, version_str: str) -> Path: ...

    class SetFlagFn(Protocol):
        def __call__(self, flag: bool) -> None: ...

    class UpdatePyprojectTomlFn(Protocol):
        def __call__(self, setting: str, value: Any) -> None: ...

    class UseCustomParserFn(Protocol):
        def __call__(self, module_import_str: str) -> type[CommitParser]: ...

    class UseHvcsFn(Protocol):
        def __call__(self, domain: str | None = None) -> type[HvcsBase]: ...

    class UseParserFn(Protocol):
        def __call__(self) -> type[CommitParser]: ...

    class UseReleaseNotesTemplateFn(Protocol):
        def __call__(self) -> None: ...


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
def dist_dir() -> Path:
    return Path("dist")


@pytest.fixture(scope="session")
def changelog_md_file() -> Path:
    return Path("CHANGELOG.md")


@pytest.fixture(scope="session")
def changelog_rst_file() -> Path:
    return Path("CHANGELOG.rst")


@pytest.fixture(scope="session")
def changelog_template_dir() -> Path:
    return Path("templates")


@pytest.fixture(scope="session")
def default_md_changelog_insertion_flag() -> str:
    return "<!-- version list -->"


@pytest.fixture(scope="session")
def default_rst_changelog_insertion_flag() -> str:
    return f"..{os.linesep}    version list"


@pytest.fixture(scope="session")
def get_wheel_file(dist_dir: Path) -> GetWheelFileFn:
    def _get_wheel_file(version_str: str) -> Path:
        return dist_dir / f"{EXAMPLE_PROJECT_NAME}-{version_str}-py3-none-any.whl"

    return _get_wheel_file


@pytest.fixture
def example_project_dir(tmp_path: Path) -> ExProjectDir:
    return tmp_path.resolve()


@pytest.fixture
def change_to_ex_proj_dir(
    example_project_dir: ExProjectDir,
) -> Generator[None, None, None]:
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
    changelog_rst_file: Path,
    cached_files_dir: Path,
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
        (changelog_rst_file, EXAMPLE_CHANGELOG_RST_CONTENT),
    ]:
        abs_filepath = cached_project_path.joinpath(file).resolve()
        # make sure the parent directory exists
        abs_filepath.parent.mkdir(parents=True, exist_ok=True)
        # write file contents
        abs_filepath.write_text(contents)

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
    copy_dir_tree(cached_example_project, example_project_dir)


@pytest.fixture
def example_project_with_release_notes_template(
    init_example_project: None,
    use_release_notes_template: UseReleaseNotesTemplateFn,
) -> None:
    use_release_notes_template()


@pytest.fixture
def use_release_notes_template(
    example_project_template_dir: Path,
    changelog_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
) -> UseReleaseNotesTemplateFn:
    def _use_release_notes_template() -> None:
        update_pyproject_toml(
            "tool.semantic_release.changelog.template_dir",
            str(changelog_template_dir),
        )
        example_project_template_dir.mkdir(parents=True, exist_ok=True)
        release_notes_j2 = example_project_template_dir / ".release_notes.md.j2"
        release_notes_j2.write_text(EXAMPLE_RELEASE_NOTES_TEMPLATE)

    return _use_release_notes_template


@pytest.fixture
def example_pyproject_toml(
    example_project_dir: ExProjectDir,
    pyproject_toml_file: Path,
) -> Path:
    return example_project_dir / pyproject_toml_file


@pytest.fixture
def example_setup_cfg(
    example_project_dir: ExProjectDir,
    setup_cfg_file: Path,
) -> Path:
    return example_project_dir / setup_cfg_file


@pytest.fixture
def example_setup_py(
    example_project_dir: ExProjectDir,
    setup_py_file: Path,
) -> Path:
    return example_project_dir / setup_py_file


@pytest.fixture
def example_dist_dir(
    example_project_dir: ExProjectDir,
    dist_dir: Path,
) -> Path:
    return example_project_dir / dist_dir


@pytest.fixture
def example_project_wheel_file(
    example_dist_dir: Path,
    get_wheel_file: GetWheelFileFn,
) -> Path:
    return example_dist_dir / get_wheel_file(EXAMPLE_PROJECT_VERSION)


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_md(
    example_project_dir: ExProjectDir,
    changelog_md_file: Path,
) -> Path:
    return example_project_dir / changelog_md_file


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_rst(
    example_project_dir: ExProjectDir,
    changelog_rst_file: Path,
) -> Path:
    return example_project_dir / changelog_rst_file


@pytest.fixture
def example_project_template_dir(
    example_project_dir: ExProjectDir,
    changelog_template_dir: Path,
) -> Path:
    return example_project_dir / changelog_template_dir


@pytest.fixture(scope="session")
def update_pyproject_toml(pyproject_toml_file: Path) -> UpdatePyprojectTomlFn:
    """Update the pyproject.toml file with the given content."""

    def _update_pyproject_toml(setting: str, value: Any) -> None:
        cwd_pyproject_toml = pyproject_toml_file.resolve()
        with open(cwd_pyproject_toml) as rfd:
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

        with open(cwd_pyproject_toml, "w") as wfd:
            tomlkit.dump(pyproject_toml, wfd)

    return _update_pyproject_toml


@pytest.fixture(scope="session")
def pyproject_toml_config_option_parser() -> str:
    return f"tool.{semantic_release.__name__}.commit_parser"


@pytest.fixture(scope="session")
def set_major_on_zero(update_pyproject_toml: UpdatePyprojectTomlFn) -> SetFlagFn:
    """Turn on/off the major_on_zero setting."""

    def _set_major_on_zero(flag: bool) -> None:
        update_pyproject_toml("tool.semantic_release.major_on_zero", flag)

    return _set_major_on_zero


@pytest.fixture(scope="session")
def set_allow_zero_version(update_pyproject_toml: UpdatePyprojectTomlFn) -> SetFlagFn:
    """Turn on/off the allow_zero_version setting."""

    def _set_allow_zero_version(flag: bool) -> None:
        update_pyproject_toml("tool.semantic_release.allow_zero_version", flag)

    return _set_allow_zero_version


@pytest.fixture(scope="session")
def use_angular_parser(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Angular parser."""

    def _use_angular_parser() -> type[CommitParser]:
        update_pyproject_toml(pyproject_toml_config_option_parser, "angular")
        return AngularCommitParser

    return _use_angular_parser


@pytest.fixture(scope="session")
def use_emoji_parser(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Emoji parser."""

    def _use_emoji_parser() -> type[CommitParser]:
        update_pyproject_toml(pyproject_toml_config_option_parser, "emoji")
        return EmojiCommitParser

    return _use_emoji_parser


@pytest.fixture(scope="session")
def use_scipy_parser(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Scipy parser."""

    def _use_scipy_parser() -> type[CommitParser]:
        update_pyproject_toml(pyproject_toml_config_option_parser, "scipy")
        return ScipyCommitParser

    return _use_scipy_parser


@pytest.fixture(scope="session")
def use_custom_parser(
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseCustomParserFn:
    """Modify the configuration file to use a user defined string parser."""

    def _use_custom_parser(module_import_str: str) -> type[CommitParser]:
        # validate this is importable before writing to parser
        module_name, attr = module_import_str.split(":", maxsplit=1)
        try:
            module = import_module(module_name)
            custom_class = getattr(module, attr)
        except (ModuleNotFoundError, AttributeError) as err:
            raise ValueError("Custom parser object not found!") from err

        update_pyproject_toml(pyproject_toml_config_option_parser, module_import_str)
        return custom_class

    return _use_custom_parser


@pytest.fixture(scope="session")
def use_github_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use GitHub as the HVCS."""

    def _use_github_hvcs(domain: str | None = None) -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "github")
        if domain is not None:
            update_pyproject_toml("tool.semantic_release.remote.domain", domain)
        return Github

    return _use_github_hvcs


@pytest.fixture(scope="session")
def use_gitlab_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use GitLab as the HVCS."""

    def _use_gitlab_hvcs(domain: str | None = None) -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "gitlab")
        if domain is not None:
            update_pyproject_toml("tool.semantic_release.remote.domain", domain)
        return Gitlab

    return _use_gitlab_hvcs


@pytest.fixture(scope="session")
def use_gitea_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use Gitea as the HVCS."""

    def _use_gitea_hvcs(domain: str | None = None) -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "gitea")
        if domain is not None:
            update_pyproject_toml("tool.semantic_release.remote.domain", domain)
        return Gitea

    return _use_gitea_hvcs


@pytest.fixture(scope="session")
def use_bitbucket_hvcs(update_pyproject_toml: UpdatePyprojectTomlFn) -> UseHvcsFn:
    """Modify the configuration file to use BitBucket as the HVCS."""

    def _use_bitbucket_hvcs(domain: str | None = None) -> type[HvcsBase]:
        update_pyproject_toml("tool.semantic_release.remote.type", "bitbucket")
        if domain is not None:
            update_pyproject_toml("tool.semantic_release.remote.domain", domain)
        return Bitbucket

    return _use_bitbucket_hvcs
