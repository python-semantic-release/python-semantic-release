import pytest

from semantic_release.commit_parser.util import parse_paragraphs


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", []),
        ("\n\n \n\n \n", []),  # Unix (LF) - empty lines
        ("\r\n\r\n \r\n\r\n \n", []),  # Windows (CRLF) - empty lines
        ("\n\nA\n\nB\n", ["A", "B"]),  # Unix (LF)
        ("\r\n\r\nA\r\n\r\nB\n", ["A", "B"]),  # Windows (CRLF)
        (
            "Long\nexplanation\n\nfull of interesting\ndetails",
            ["Long explanation", "full of interesting details"],
        ),
        (
            # Windows uses CRLF
            "Long\r\nexplanation\r\n\r\nfull of interesting\r\ndetails",
            ["Long explanation", "full of interesting details"],
        ),
    ],
)
def test_parse_paragraphs(text, expected):
    assert parse_paragraphs(text) == expected
