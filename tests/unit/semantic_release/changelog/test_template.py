from __future__ import annotations

# TODO: This tests for the main options that will help configuring a template,
# but not all of them. The testing can be expanded to cover all the options later.
# It's not super essential as Jinja2 does most of the testing, we're just checking
# that we can properly set the right strings in the template environment.
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from semantic_release.changelog.template import environment

if TYPE_CHECKING:
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
