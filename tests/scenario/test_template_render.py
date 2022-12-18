import itertools
import os
from pathlib import Path

import pytest

from semantic_release.changelog.template import environment, recursive_render

NORMAL_TEMPLATE_SRC = """---
content:
    - a string
    - ["a nested list"]
vars:
    # a comment
    hello: {{ "world" | upper }}

"""

NORMAL_TEMPLATE_RENDERED = """---
content:
    - a string
    - ["a nested list"]
vars:
    # a comment
    hello: WORLD
"""

PLAINTEXT_FILE_CONTENT = """
I should not be rendered as a template.
{{ "this string should be untouched" | upper }}
"""


def _strip_trailing_j2(path: Path) -> Path:
    if path.name.endswith(".j2"):
        return path.with_name(path.name[:-3])
    return path


@pytest.fixture
def normal_template(example_project_template_dir):
    template = example_project_template_dir / "normal.yaml.j2"
    template.write_text(NORMAL_TEMPLATE_SRC)
    yield template


@pytest.fixture
def long_directory_path(example_project_template_dir):
    # NOTE: fixture enables using Path rather than
    # constant string, so no issue with / vs \ on Windows
    d = example_project_template_dir / "long" / "dir" / "path"
    os.makedirs(str(d.resolve()), exist_ok=True)
    yield d


@pytest.fixture
def deeply_nested_file(long_directory_path):
    file = long_directory_path / "buried.txt"
    file.write_text(PLAINTEXT_FILE_CONTENT)
    yield file


@pytest.fixture
def hidden_file(example_project_template_dir):
    file = example_project_template_dir / ".hidden"
    file.write_text("I shouldn't be present")
    yield file


@pytest.fixture
def directory_path_with_hidden_subfolder(example_project_template_dir):
    d = example_project_template_dir / "path" / ".subfolder" / "hidden"
    os.makedirs(str(d.resolve()), exist_ok=True)
    yield d


@pytest.fixture
def excluded_file(directory_path_with_hidden_subfolder):
    file = directory_path_with_hidden_subfolder / "excluded.txt"
    file.write_text("I shouldn't be present")
    yield file


def test_recursive_render(
    example_project,
    example_project_template_dir,
    normal_template,
    deeply_nested_file,
    hidden_file,
    excluded_file,
):
    tmpl_dir = str(example_project_template_dir.resolve())
    env = environment(template_dir=tmpl_dir)

    preexisting_paths = set(example_project.rglob("**/*"))

    recursive_render(
        template_dir=str(tmpl_dir),
        environment=env,
        _root_dir=str(example_project.resolve()),
    )
    rendered_normal_template = _strip_trailing_j2(
        example_project / normal_template.relative_to(example_project_template_dir)
    )
    assert rendered_normal_template.exists()
    assert rendered_normal_template.read_text() == NORMAL_TEMPLATE_RENDERED

    rendered_deeply_nested = example_project / deeply_nested_file.relative_to(
        example_project_template_dir
    )
    assert rendered_deeply_nested.exists()
    assert rendered_deeply_nested.read_text() == PLAINTEXT_FILE_CONTENT

    rendered_hidden = example_project / hidden_file.relative_to(
        example_project_template_dir
    )
    assert not rendered_hidden.exists()

    assert not (example_project / "path").exists()

    assert set(example_project.rglob("**/*")) == preexisting_paths.union(
        (
            example_project / p
            for t in (
                rendered_normal_template,
                rendered_deeply_nested,
            )
            for p in itertools.accumulate(
                t.relative_to(example_project).parts, func=lambda *a: os.sep.join(a)
            )
        )
    )
