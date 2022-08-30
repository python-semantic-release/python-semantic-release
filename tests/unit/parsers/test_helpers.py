from semantic_release.history.parser_helpers import parse_paragraphs


def test_parse_paragraphs_with_no_content():
    paragraphs = parse_paragraphs("")
    assert len(paragraphs) == 0


def test_parse_paragraphs():
    paragraphs = parse_paragraphs("Paragraph 0\n\nParagraph 1")
    assert len(paragraphs) == 2
    assert paragraphs[0] == "Paragraph 0"
    assert paragraphs[1] == "Paragraph 1"


def test_parse_paragraphs_multiline():
    paragraphs = parse_paragraphs("This paragraph is over\nmultiple lines.")
    assert paragraphs[0] == "This paragraph is over multiple lines."
