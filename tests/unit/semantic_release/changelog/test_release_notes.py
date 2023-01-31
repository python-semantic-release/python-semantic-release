# NOTE: use backport with newer API
from datetime import datetime

from importlib_resources import files

from semantic_release.changelog.context import make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.changelog.template import environment
from semantic_release.hvcs import Github
from semantic_release.version import Version, VersionTranslator

from tests.const import COMMIT_MESSAGE

default_release_notes_template = (
    files("tests")
    .joinpath("unit/semantic_release/changelog/test_release_notes.md.j2")
    .read_text(encoding="utf-8")
)

today_as_str = datetime.now().strftime("%Y-%m-%d")


def _cm_rstripped(version: str) -> str:
    return COMMIT_MESSAGE.format(version=version).rstrip()


EXPECTED_CONTENT = f"""\
# v1.1.0-alpha.3 ({today_as_str})
## Fix
* fix: (feature) add some more text
## Unknown
* {_cm_rstripped("1.1.0-alpha.3")}
"""


def test_default_changelog_template(
    repo_with_git_flow_and_release_channels_angular_commits, default_angular_parser
):
    version = Version.parse("1.1.0-alpha.3")
    repo = repo_with_git_flow_and_release_channels_angular_commits
    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    rh = ReleaseHistory.from_git_history(
        repo=repo, translator=VersionTranslator(), commit_parser=default_angular_parser
    )
    context = make_changelog_context(
        hvcs_client=Github(remote_url=repo.remote().url), release_history=rh
    )
    context.bind_to_environment(env)
    release = rh.released[version]
    actual_content = env.from_string(default_release_notes_template).render(
        version=version, release=release
    )
    assert actual_content == EXPECTED_CONTENT
