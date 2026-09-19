from __future__ import annotations

# TODO: This tests for the main options that will help configuring a template,
# but not all of them. The testing can be expanded to cover all the options later.
# It's not super essential as Jinja2 does most of the testing, we're just checking
# that we can properly set the right strings in the template environment.
from re import compile as regexp
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from fsspec.implementations.memory import (  # type: ignore[import-untyped]
    MemoryFileSystem,
)
from jinja2 import TemplateNotFound
from upath import UPath

from semantic_release.changelog.template import (
    UPathLoader,
    environment,
    recursive_render,
)

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

EXAMPLE_TEMPLATE_FORMAT_STR = """
<h1>This is an example template document</h1>

<h2>The title is {variable_start_string} title | upper {variable_end_string}</h2>
{comment_start_string}- This text should not appear {comment_end_string}
{block_start_string}- for subject in subjects {block_end_string}
<p>This is a paragraph about {variable_start_string} subject {variable_end_string}</p>
{block_start_string}- endfor {block_end_string}"""


@pytest.mark.parametrize(
    "format_map",
    [
        {
            "block_start_string": "{%",
            "block_end_string": "%}",
            "variable_start_string": "{{",
            "variable_end_string": "}}",
            "comment_start_string": "{#",
            "comment_end_string": "#}",
        },
        {
            "block_start_string": "{[",
            "block_end_string": "]}",
            "variable_start_string": "{{",
            "variable_end_string": "}}",
            "comment_start_string": "/*",
            "comment_end_string": "*/",
        },
    ],
)
@pytest.mark.parametrize(
    "subjects", [("dogs", "cats"), ("stocks", "finance", "politics")]
)
def test_template_env_configurable(format_map: dict[str, Any], subjects: tuple[str]):
    template_as_str = EXAMPLE_TEMPLATE_FORMAT_STR.format_map(format_map)
    env = environment(**format_map)
    template = env.from_string(template_as_str)

    title = "important"
    newline = "\n"
    expected_result = dedent(
        f"""
        <h1>This is an example template document</h1>

        <h2>The title is {title.upper()}</h2>
        {(newline + " " * 8).join(f'<p>This is a paragraph about {subject}</p>' for subject in subjects)}"""  # noqa: E501
    )
    actual_result = template.render(title="important", subjects=subjects)

    assert expected_result == actual_result


def test_upathloader_get_source_existing_template(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "test.j2"
    template_content = "Hello {{ name }}"
    template_file.write_text(template_content)
    loader = UPathLoader(UPath(template_dir))

    source, path, uptodate = loader.get_source(MagicMock(), "test.j2")

    assert source == template_content
    assert str(template_dir / "test.j2") in path
    assert uptodate() is True


def test_upathloader_get_source_missing_template_raises(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    loader = UPathLoader(UPath(template_dir))

    with pytest.raises(TemplateNotFound, match=regexp(r"nonexistent\.j2")):
        loader.get_source(MagicMock(), "nonexistent.j2")


def test_upathloader_get_source_nested_template(tmp_path: Path):
    template_dir = tmp_path / "templates"
    nested_dir = template_dir / "subdir" / "nested"
    nested_dir.mkdir(parents=True)
    template_file = nested_dir / "deep.j2"
    template_file.write_text("Deep template")
    loader = UPathLoader(UPath(template_dir))

    source, _, _ = loader.get_source(MagicMock(), "subdir/nested/deep.j2")

    assert source == "Deep template"


def test_upathloader_list_templates_empty_directory(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    loader = UPathLoader(UPath(template_dir))

    templates = loader.list_templates()

    assert templates == []


def test_upathloader_list_templates_flat_structure(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "a.j2").write_text("A")
    (template_dir / "b.html").write_text("B")
    (template_dir / "c.txt").write_text("C")
    loader = UPathLoader(UPath(template_dir))

    templates = loader.list_templates()

    assert sorted(templates) == ["a.j2", "b.html", "c.txt"]


def test_upathloader_list_templates_nested_structure(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "root.j2").write_text("Root")
    subdir = template_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.j2").write_text("Nested")
    loader = UPathLoader(UPath(template_dir))

    templates = loader.list_templates()

    assert "root.j2" in templates
    assert any("subdir" in t and "nested.j2" in t for t in templates)


def test_upathloader_list_templates_excludes_directories(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "file.j2").write_text("File")
    (template_dir / "subdir").mkdir()
    loader = UPathLoader(UPath(template_dir))

    templates = loader.list_templates()

    assert templates == ["file.j2"]


def test_upathloader_custom_encoding(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "unicode.j2"
    content = "Unicode: \u00e9\u00e8\u00ea"
    template_file.write_text(content, encoding="utf-8")
    loader = UPathLoader(UPath(template_dir), encoding="utf-8")

    source, _, _ = loader.get_source(MagicMock(), "unicode.j2")

    assert source == content


@pytest.fixture
def clear_memory_fs():
    # MemoryFileSystem uses a shared store, so we need to clear it
    MemoryFileSystem.store.clear()
    MemoryFileSystem.pseudo_dirs.clear()
    yield
    MemoryFileSystem.store.clear()
    MemoryFileSystem.pseudo_dirs.clear()


@pytest.fixture
def memory_fs(clear_memory_fs: None) -> MemoryFileSystem:
    return MemoryFileSystem()


def test_upathloader_with_memory_filesystem(memory_fs: MemoryFileSystem):
    memory_fs.mkdir("/templates")
    memory_fs.pipe("/templates/test.j2", b"Hello {{ name }}")
    upath = UPath("memory:///templates")
    loader = UPathLoader(upath)

    source, path, _ = loader.get_source(MagicMock(), "test.j2")

    assert source == "Hello {{ name }}"
    assert "test.j2" in path


def test_upathloader_list_templates_memory_filesystem(memory_fs: MemoryFileSystem):
    memory_fs.mkdir("/templates")
    memory_fs.pipe("/templates/a.j2", b"A")
    memory_fs.pipe("/templates/b.j2", b"B")
    upath = UPath("memory:///templates")
    loader = UPathLoader(upath)

    templates = loader.list_templates()

    assert sorted(templates) == ["a.j2", "b.j2"]


def test_upathloader_nested_memory_filesystem(memory_fs: MemoryFileSystem):
    memory_fs.mkdir("/templates")
    memory_fs.mkdir("/templates/subdir")
    memory_fs.pipe("/templates/subdir/nested.j2", b"Nested content")
    upath = UPath("memory:///templates")
    loader = UPathLoader(upath)

    source, _, _ = loader.get_source(MagicMock(), "subdir/nested.j2")

    assert source == "Nested content"


def test_environment_with_memory_filesystem(memory_fs: MemoryFileSystem):
    memory_fs.mkdir("/templates")
    memory_fs.pipe("/templates/greet.j2", b"Hello, {{ name }}!")
    upath = UPath("memory:///templates")
    env = environment(template_dir=upath)

    template = env.get_template("greet.j2")
    result = template.render(name="Remote")

    assert result == "Hello, Remote!"


def test_recursive_render_with_memory_filesystem(
    memory_fs: MemoryFileSystem, tmp_path: Path
):
    memory_fs.mkdir("/templates")
    memory_fs.pipe("/templates/config.yaml.j2", b"key: {{ value }}")
    memory_fs.pipe("/templates/readme.txt", b"Static file")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    upath = UPath("memory:///templates")
    env = environment(template_dir=upath)
    env.globals["value"] = "test_value"

    rendered_paths = recursive_render(
        template_dir=upath,
        environment=env,
        _root_dir=output_dir,
    )

    assert len(rendered_paths) == 2
    assert (output_dir / "config.yaml").exists()
    assert "key: test_value" in (output_dir / "config.yaml").read_text()
    assert (output_dir / "readme.txt").exists()
    assert (output_dir / "readme.txt").read_text() == "Static file"


def test_upathloader_missing_template_memory_filesystem(memory_fs: MemoryFileSystem):
    memory_fs.mkdir("/templates")
    upath = UPath("memory:///templates")
    loader = UPathLoader(upath)

    with pytest.raises(TemplateNotFound, match=regexp(r"missing\.j2")):
        loader.get_source(MagicMock(), "missing.j2")
