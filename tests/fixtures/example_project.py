from textwrap import dedent

import pytest

from tests.const import (
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_SETUP_PY_CONTENT,
    EXAMPLE_SETUP_CFG_CONTENT,
)


@pytest.fixture
def example_project(tmp_path):
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
            from __future__ import annotations


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
