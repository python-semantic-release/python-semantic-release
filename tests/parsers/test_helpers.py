from semantic_release.history.parser_helpers import parse_text_block


def test_parse_text_block_with_no_content():
    body, parse = parse_text_block("")

    assert body == ""
    assert parse == ""


def test_parse_text_block_with_only_body():
    body, parse = parse_text_block("This is a body paragraph.")

    assert body == "This is a body paragraph."
    assert parse == ""


def test_parse_text_block_with_body_and_footer():
    body, parse = parse_text_block(
        "This is a body paragraph.\n\n...and this is a footer"
    )

    assert body == "This is a body paragraph."
    assert parse == "...and this is a footer"


def test_parse_text_block_with_multiline_body_and_multiline_footer():
    body, parse = parse_text_block(
        "This is a body\nparagraph.\n\n...and this is\na footer"
    )

    assert body == "This is a body paragraph."
    assert parse == "...and this is a footer"
