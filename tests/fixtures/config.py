import pytest

from tests.const import EXAMPLE_PYPROJECT_TOML_CONTENT


@pytest.fixture
def example_pyproject_toml(tmp_path):
    fn = tmp_path / "pyproject.toml"
    fn.write_text(EXAMPLE_PYPROJECT_TOML_CONTENT)
    return fn
