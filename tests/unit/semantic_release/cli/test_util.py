import json
from textwrap import dedent

import pytest
from pytest import lazy_fixture

from semantic_release.cli.util import load_raw_config_file, parse_toml
from semantic_release.errors import InvalidConfiguration


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
def test_parse_toml(toml_text, expected):
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
def raw_toml_config_file(tmp_path):
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

    yield path


@pytest.fixture
def raw_pyproject_toml_config_file(tmp_path):
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / "pyproject.toml"

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

    yield path


@pytest.fixture
def raw_json_config_file(tmp_path):
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / ".releaserc"

    path.write_text(
        json.dumps(
            {"semantic_release": {"foo": "bar", "abc": {"bar": "baz"}}}, indent=4
        )
    )

    yield path


@pytest.fixture
def invalid_toml_config_file(tmp_path):
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

    yield path


@pytest.fixture
def invalid_json_config_file(tmp_path):
    tmp_path.mkdir(exist_ok=True)

    path = tmp_path / "releaserc.json"

    path.write_text(
        dedent(
            r"""
            {"semantic_release": {foo: "bar", "abc": {bar: "baz"}}}
            """
        )
    )

    yield path


@pytest.fixture
def invalid_other_config_file(tmp_path):
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

    yield path


@pytest.mark.parametrize(
    "raw_config_file, expected",
    [
        (lazy_fixture("raw_toml_config_file"), {"foo": "bar", "abc": {"bar": "baz"}}),
        (
            lazy_fixture("raw_pyproject_toml_config_file"),
            {"foo": "bar", "abc": {"bar": "baz"}},
        ),
        (
            lazy_fixture("raw_json_config_file"),
            {"semantic_release": {"foo": "bar", "abc": {"bar": "baz"}}},
        ),
    ],
)
def test_load_raw_config_file_loads_config(raw_config_file, expected):
    assert load_raw_config_file(raw_config_file) == expected


@pytest.mark.parametrize(
    "raw_config_file",
    [
        lazy_fixture("invalid_toml_config_file"),
        lazy_fixture("invalid_json_config_file"),
        lazy_fixture("invalid_other_config_file"),
    ],
)
def test_load_raw_config_file_loads_config(raw_config_file):
    with pytest.raises(InvalidConfiguration):
        load_raw_config_file(raw_config_file)
