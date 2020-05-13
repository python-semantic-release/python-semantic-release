
from semantic_release.history import emoji_parser

def test_major():
    commit = ":boom: Breaking changes"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 3
    assert parsed_commit[1] == ":boom:"
    assert parsed_commit[3] == [":boom: Breaking changes"]


def test_minor():
    commit = ":sparkles: Add a new feature"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [":sparkles: Add a new feature"]


def test_patch():
    commit = ":bug: Fixing a bug"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 1
    assert parsed_commit[1] == ":bug:"
    assert parsed_commit[3] == [":bug: Fixing a bug"]

def test_other_emoji():
    commit = ":pencil: Documentation changes"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 0
    assert parsed_commit[1] == "Other"
    assert parsed_commit[3] == [":pencil: Documentation changes"]

def test_multiple_emojis():
    commit = ":sparkles::pencil: Add a feature and document it"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [":sparkles::pencil: Add a feature and document it"]

def test_emoji_in_description():
    commit = (
        ":sparkles: Add a new feature\n\n"
        ":boom: should not be detected"
    )
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [
        ":sparkles: Add a new feature",
        ":boom: should not be detected"
    ]
