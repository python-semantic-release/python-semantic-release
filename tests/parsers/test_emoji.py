import mock
import pytest

from semantic_release.history import emoji_parser

from .. import wrapped_config_get


def test_major():
    commit = (
        ":boom: Breaking changes\n\n" "More description\n\n" "Even more description"
    )
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 3
    assert parsed_commit[1] == ":boom:"
    assert parsed_commit[3] == [
        ":boom: Breaking changes",
        "More description",
        "Even more description",
    ]
    assert parsed_commit[4] == ["More description", "Even more description"]


def test_minor():
    commit = ":sparkles: Add a new feature\n\n" "Some description of the feature"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [
        ":sparkles: Add a new feature",
        "Some description of the feature",
    ]
    assert parsed_commit[4] == []


def test_patch():
    commit = ":bug: Fixing a bug\n\n" "The bug is finally gone!"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 1
    assert parsed_commit[1] == ":bug:"
    assert parsed_commit[3] == [":bug: Fixing a bug", "The bug is finally gone!"]
    assert parsed_commit[4] == []


def test_other_emoji():
    commit = ":pencil: Documentation changes"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 0
    assert parsed_commit[1] == "Other"
    assert parsed_commit[3] == [":pencil: Documentation changes"]
    assert parsed_commit[4] == []


def test_multiple_emojis():
    commit = ":sparkles::pencil: Add a feature and document it"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [":sparkles::pencil: Add a feature and document it"]
    assert parsed_commit[4] == []


def test_emoji_in_description():
    commit = ":sparkles: Add a new feature\n\n" ":boom: should not be detected"
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == 2
    assert parsed_commit[1] == ":sparkles:"
    assert parsed_commit[3] == [
        ":sparkles: Add a new feature",
        ":boom: should not be detected",
    ]
    assert parsed_commit[4] == []


@mock.patch(
    "semantic_release.history.parser_emoji.config.get",
    wrapped_config_get(use_textual_changelog_sections=True),
)
@pytest.mark.parametrize(
    "level,commit,commit_type",
    [
        (
            3,
            ":boom: Breaking changes\n\n"
            "More description\n\n"
            "Even more description",
            "breaking",
        ),
        (
            2,
            ":sparkles: Add a new feature\n\n" "Some description of the feature",
            "feature",
        ),
        (
            1,
            ":bug: Fixing a bug\n\n" "The bug is finally gone!",
            "fix",
        ),
    ],
)
def test_use_textual_changelog_sections(level, commit, commit_type):
    parsed_commit = emoji_parser(commit)
    assert parsed_commit[0] == level
    assert parsed_commit[1] == commit_type
