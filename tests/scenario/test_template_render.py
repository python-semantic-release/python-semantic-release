from __future__ import annotations

import itertools
import os
from typing import TYPE_CHECKING

import pytest

from semantic_release.changelog.template import environment, recursive_render

if TYPE_CHECKING:
    from pathlib import Path

    from tests.fixtures.example_project import ExProjectDir


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
def normal_template(example_project_template_dir: Path) -> Path:
    template = example_project_template_dir / "normal.yaml.j2"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(NORMAL_TEMPLATE_SRC)
    return template


@pytest.fixture
def long_directory_path(example_project_template_dir: Path) -> Path:
    # NOTE: fixture enables using Path rather than
    # constant string, so no issue with / vs \ on Windows
    return example_project_template_dir / "long" / "dir" / "path"


@pytest.fixture
def deeply_nested_file(long_directory_path: Path) -> Path:
    file = long_directory_path / "buried.txt"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(PLAINTEXT_FILE_CONTENT)
    return file


@pytest.fixture
def hidden_file(example_project_template_dir: Path) -> Path:
    file = example_project_template_dir / ".hidden"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("I shouldn't be present")
    return file


@pytest.fixture
def directory_path_with_hidden_subfolder(example_project_template_dir: Path) -> Path:
    return example_project_template_dir / "path" / ".subfolder" / "hidden"


@pytest.fixture
def excluded_file(directory_path_with_hidden_subfolder: Path) -> Path:
    file = directory_path_with_hidden_subfolder / "excluded.txt"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("I shouldn't be present")
    return file


@pytest.mark.usefixtures(excluded_file.__name__)
def test_recursive_render(
    init_example_project: None,
    example_project_dir: Path,
    example_project_template_dir: Path,
    normal_template,
    deeply_nested_file,
    hidden_file,
):
    tmpl_dir = str(example_project_template_dir.resolve())
    env = environment(template_dir=tmpl_dir)

    preexisting_paths = set(example_project_dir.rglob("**/*"))

    recursive_render(
        template_dir=example_project_template_dir.resolve(),
        environment=env,
        _root_dir=str(example_project_dir.resolve()),
    )
    rendered_normal_template = _strip_trailing_j2(
        example_project_dir / normal_template.relative_to(example_project_template_dir)
    )
    assert rendered_normal_template.exists()
    assert rendered_normal_template.read_text() == NORMAL_TEMPLATE_RENDERED

    rendered_deeply_nested = example_project_dir / deeply_nested_file.relative_to(
        example_project_template_dir
    )
    assert rendered_deeply_nested.exists()
    assert rendered_deeply_nested.read_text() == PLAINTEXT_FILE_CONTENT

    rendered_hidden = example_project_dir / hidden_file.relative_to(
        example_project_template_dir
    )
    assert not rendered_hidden.exists()

    assert not (example_project_dir / "path").exists()

    assert set(example_project_dir.rglob("**/*")) == preexisting_paths.union(
        example_project_dir / p
        for t in (
            rendered_normal_template,
            rendered_deeply_nested,
        )
        for p in itertools.accumulate(
            t.relative_to(example_project_dir).parts, func=lambda *a: os.sep.join(a)
        )
    )


@pytest.fixture
def dotfolder_template_dir(example_project_dir: ExProjectDir) -> Path:
    return example_project_dir / ".templates/.psr-templates"


@pytest.fixture
def dotfolder_template(
    init_example_project: None, dotfolder_template_dir: Path
) -> Path:
    tmpl = dotfolder_template_dir / "template.txt"
    tmpl.parent.mkdir(parents=True, exist_ok=True)
    tmpl.write_text("I am a template")
    return tmpl


def test_recursive_render_with_top_level_dotfolder(
    init_example_project: None,
    example_project_dir: ExProjectDir,
    dotfolder_template: Path,
    dotfolder_template_dir: Path,
):
    preexisting_paths = set(example_project_dir.rglob("**/*"))
    env = environment(template_dir=dotfolder_template_dir.resolve())

    recursive_render(
        template_dir=dotfolder_template_dir.resolve(),
        environment=env,
        _root_dir=example_project_dir.resolve(),
    )

    rendered_template = example_project_dir / dotfolder_template.name
    assert rendered_template.exists()

    assert set(example_project_dir.rglob("**/*")) == preexisting_paths.union(
        {example_project_dir / rendered_template}
    )
