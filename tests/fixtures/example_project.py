import os
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from typing import Generator

import pytest

from tests.const import (
    EXAMPLE_CHANGELOG_MD_CONTENT,
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_SETUP_CFG_CONTENT,
    EXAMPLE_SETUP_PY_CONTENT,
)


@contextmanager
def cd(path: Path) -> Generator[Path, None, None]:
    cwd = os.getcwd()
    os.chdir(str(path.resolve()))
    yield path
    os.chdir(cwd)


@pytest.fixture
def example_project(tmp_path):
    with cd(tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        example_dir = src_dir / EXAMPLE_PROJECT_NAME
        example_dir.mkdir()
        init_py = example_dir / "__init__.py"
        init_py.write_text(
            dedent(
                f'''
                """
                An example package with a very informative docstring
                """
                __version__ = "{EXAMPLE_PROJECT_VERSION}"


                def hello_world() -> None:
                    print("Hello World")
                '''
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
        yield tmp_path


@pytest.fixture
def example_pyproject_toml(example_project):
    yield example_project / "pyproject.toml"


@pytest.fixture
def example_setup_cfg(example_project):
    yield example_project / "setup.cfg"


@pytest.fixture
def example_setup_py(example_project):
    yield example_project / "setup.py"


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_md(example_project):
    yield example_project / "CHANGELOG.md"


@pytest.fixture
def example_project_template_dir(example_project):
    yield example_project / "templates"
