from __future__ import annotations

import json
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.cli.util import load_raw_config_file, parse_toml
from semantic_release.errors import InvalidConfiguration

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


@pytest.mark.parametrize(
    "toml_text, expected",
    [
        (
            dedent(
                r"""
                [not_the_right_key]
                foo = "bar"
                """
            ),
            {},
        ),
        (
            dedent(
                r"""
                [semantic_release]
                foo = "bar"
                """
            ),
            {"foo": "bar"},
        ),
        (
            dedent(
                r"""
                [tool.semantic_release]
                abc = 123

                [tool.semantic_release.foo]
                def = 456
                """
            ),
            {"abc": 123, "foo": {"def": 456}},
        ),
    ],
)
def test_parse_toml(toml_text: str, expected: dict[str, Any]):
    assert parse_toml(toml_text) == expected


def test_parse_toml_raises_invalid_configuration_with_invalid_toml():
    invalid_toml = dedent(
        r"""
        [semantic_release]
        foo = bar  # this is not a valid TOML string
        """
    )

    with pytest.raises(InvalidConfiguration):
        parse_toml(invalid_toml)


@pytest.fixture
def raw_toml_config_file(tmp_path: Path) -> Path:
    path = tmp_path / "config.toml"

    path.write_text(
        dedent(
            r"""
            [semantic_release]
            foo = "bar"

            [semantic_release.abc]
            bar = "baz"
            """
        )
    )

    return path


@pytest.fixture
def raw_pyproject_toml_config_file(tmp_path: Path, pyproject_toml_file: Path) -> Path:
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / pyproject_toml_file

    path.write_text(
        dedent(
            r"""
            [tool.semantic_release]
            foo = "bar"

            [tool.semantic_release.abc]
            bar = "baz"
            """
        )
    )

    return path


@pytest.fixture
def raw_json_config_file(tmp_path: Path) -> Path:
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / ".releaserc"

    path.write_text(
        json.dumps(
            {"semantic_release": {"foo": "bar", "abc": {"bar": "baz"}}}, indent=4
        )
    )

    return path


@pytest.fixture
def invalid_toml_config_file(tmp_path: Path) -> Path:
    path = tmp_path / "config.toml"

    path.write_text(
        dedent(
            r"""
            [semantic_release]
            foo = bar  # no quotes == invalid

            [semantic_release.abc]
            bar = "baz"
            """
        )
    )

    return path


@pytest.fixture
def invalid_json_config_file(tmp_path: Path) -> Path:
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / "releaserc.json"

    path.write_text(
        dedent(
            r"""
            {"semantic_release": {foo: "bar", "abc": {bar: "baz"}}}
            """
        )
    )

    return path


@pytest.fixture
def invalid_other_config_file(tmp_path: Path) -> Path:
    # e.g. XML
    path = tmp_path / "config.xml"

    path.write_text(
        dedent(
            r"""
            <semantic_release>
                <foo>bar</foo>
                <abc>
                    <bar>baz</bar>
                </abc>
            </semantic_release>
            """
        )
    )

    return path


@pytest.mark.parametrize(
    "raw_config_file, expected",
    [
        (
            lazy_fixture(raw_toml_config_file.__name__),
            {"foo": "bar", "abc": {"bar": "baz"}},
        ),
        (
            lazy_fixture(raw_pyproject_toml_config_file.__name__),
            {"foo": "bar", "abc": {"bar": "baz"}},
        ),
        (
            lazy_fixture(raw_json_config_file.__name__),
            {"foo": "bar", "abc": {"bar": "baz"}},
        ),
    ],
)
def test_load_raw_config_file_loads_config(
    raw_config_file: Path, expected: dict[str, Any]
):
    assert load_raw_config_file(raw_config_file) == expected


@pytest.mark.parametrize(
    "raw_config_file",
    [
        lazy_fixture(invalid_toml_config_file.__name__),
        lazy_fixture(invalid_json_config_file.__name__),
        lazy_fixture(invalid_other_config_file.__name__),
    ],
)
def test_load_raw_invalid_config_file_raises_error(raw_config_file: Path):
    with pytest.raises(InvalidConfiguration):
        load_raw_config_file(raw_config_file)
