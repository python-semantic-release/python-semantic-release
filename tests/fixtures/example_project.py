import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Generator

import pytest
import tomlkit

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

    ExProjectDir = Path

    class UpdatePyprojectTomlFn(Protocol):
        def __call__(self, setting: str, value: "Any") -> None:
            ...


@pytest.fixture
def change_to_tmp_dir(tmp_path: "Path") -> "Generator[None, None, None]":
    cwd = os.getcwd()
    os.chdir(str(tmp_path.resolve()))
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def example_project(change_to_tmp_dir: None) -> "ExProjectDir":
    tmp_path = Path.cwd()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    example_dir = src_dir / EXAMPLE_PROJECT_NAME
    example_dir.mkdir()
    init_py = example_dir / "__init__.py"
    init_py.write_text(
        dedent(
            '''
            """
            An example package with a very informative docstring
            """
            from ._version import __version__


            def hello_world() -> None:
                print("Hello World")
            '''
        )
    )
    version_py = example_dir / "_version.py"
    version_py.write_text(
        dedent(
            f"""
            __version__ = "{EXAMPLE_PROJECT_VERSION}"
            """
        )
    )
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(
        dedent(
            f"""
            *.pyc
            /src/**/{version_py.name}
            """
        )
    )
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(EXAMPLE_PYPROJECT_TOML_CONTENT)
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(EXAMPLE_SETUP_CFG_CONTENT)
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(EXAMPLE_SETUP_PY_CONTENT)
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    changelog_md = tmp_path / "CHANGELOG.md"
    changelog_md.write_text(EXAMPLE_CHANGELOG_MD_CONTENT)
    return tmp_path


@pytest.fixture
def example_project_with_release_notes_template(example_project: Path) -> Path:
    template_dir = example_project / "templates"
    release_notes_j2 = template_dir / ".release_notes.md.j2"
    release_notes_j2.write_text(EXAMPLE_RELEASE_NOTES_TEMPLATE)
    return example_project


@pytest.fixture
def example_pyproject_toml(example_project):
    return example_project / "pyproject.toml"


@pytest.fixture
def example_setup_cfg(example_project):
    return example_project / "setup.cfg"


@pytest.fixture
def example_setup_py(example_project):
    return example_project / "setup.py"


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_md(example_project):
    return example_project / "CHANGELOG.md"


@pytest.fixture
def example_project_template_dir(example_project):
    return example_project / "templates"


@pytest.fixture
def update_pyproject_toml(
    example_project: "Path", example_pyproject_toml: "Path"
) -> "UpdatePyprojectTomlFn":
    """Update the pyproject.toml file with the given content."""
    def _update_pyproject_toml(setting: str, value: "Any") -> None:
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

        with open(example_pyproject_toml, 'w') as wfd:
            tomlkit.dump(pyproject_toml, wfd)

    return _update_pyproject_toml
