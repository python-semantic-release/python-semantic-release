import pytest

from semantic_release.errors import UnknownCommitMessageStyleError
from semantic_release.history import tag_parser

text = 'This is an long explanatory part of a commit message. It should give ' \
       'some insight to the fix this commit adds to the codebase.'
footer = 'Closes #400'


def test_parser_raises_unknown_message_style():
    pytest.raises(UnknownCommitMessageStyleError, tag_parser, '')


def test_parser_return_correct_bump_level():
    assert tag_parser(':guardsman: Remove emoji parser')[0] == 3
    assert tag_parser(':feature: Add emoji parser')[0] == 3
    assert tag_parser(':nut_and_bolt: Fix regex in angular parser')[0] == 1
    assert tag_parser('Add a test for angular parser')[0] == 0


def test_parser_return_type_from_commit_message():
    assert tag_parser(':guardsman: ...')[1] == 'breaking'
    assert tag_parser(':sparkles: ...')[1] == 'feature'
    assert tag_parser(':nut_and_bolt: ...')[1] == 'fix'


def test_parser_return_subject_from_commit_message():
    assert (
        tag_parser(':sparkles: Add emoji parser')[3][0]
        ==
        'Add emoji parser'
    )


def test_parser_return_text_from_commit_message():
    assert (
        tag_parser(':nut_and_bolt: Fix regex in an parser\n\n{}'.format(text))[3][1]
        ==
        text
    )


def test_parser_return_footer_from_commit_message():
    assert (
        tag_parser(':nut_and_bolt: Fix env \n\n{t[text]}\n\n{t[footer]}'.format(t=globals()))[3][2]
        ==
        footer
    )
