import pytest

from semantic_release.commit_parser.util import parse_paragraphs


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", []),
        ("\n\n \n\n \n", [" ", "  "]),
        (
            "Long\nexplanation\n\nfull of interesting\ndetails",
            ["Long explanation", "full of interesting details"],
        ),
    ],
)
def test_parse_paragraphs(text, expected):
    assert parse_paragraphs(text) == expected
