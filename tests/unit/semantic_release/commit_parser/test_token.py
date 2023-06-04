from semantic_release import LevelBump
from semantic_release.commit_parser import ParsedCommit

from tests.unit.semantic_release.commit_parser.helper import make_commit


def test_parsed_commit_computed_properties():
    message = "feat(parser): Add new parser pattern"
    commit = make_commit(message)

    token = ParsedCommit(
        bump=LevelBump.MINOR,
        type="feature",
        scope="parser",
        descriptions=["Add new parser pattern"],
        breaking_descriptions=[],
        commit=commit,
    )

    assert token.message == message
    assert token.hexsha == commit.hexsha
    assert token.short_hash == commit.hexsha[:7]
