# NOTE: use backport with newer API
from datetime import datetime

from importlib_resources import files

from semantic_release.changelog.context import make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.changelog.template import environment
from semantic_release.hvcs import Github
from semantic_release.version.translator import VersionTranslator

from tests.const import COMMIT_MESSAGE

default_changelog_template = (
    files("tests")
    .joinpath("unit/semantic_release/changelog/TEST_CHANGELOG.md.j2")
    .read_text(encoding="utf-8")
)

today_as_str = datetime.now().strftime("%Y-%m-%d")


def _cm_rstripped(version: str) -> str:
    return COMMIT_MESSAGE.format(version=version).rstrip()


EXPECTED_CONTENT = f"""\
# CHANGELOG
## v1.1.0-alpha.3 ({today_as_str})
### Fix
* fix: (feature) add some more text
### Unknown
* {_cm_rstripped("1.1.0-alpha.3")}
## v1.1.0-alpha.2 ({today_as_str})
### Feature
* feat: (feature) add some more text
### Unknown
* {_cm_rstripped("1.1.0-alpha.2")}
## v1.1.0-alpha.1 ({today_as_str})
### Feature
* feat: (feature) add some more text
### Unknown
* {_cm_rstripped("1.1.0-alpha.1")}
## v1.1.0-rc.2 ({today_as_str})
### Fix
* fix: (dev) add some more text
### Unknown
* {_cm_rstripped("1.1.0-rc.2")}
## v1.1.0-rc.1 ({today_as_str})
### Feature
* feat: (dev) add some more text
### Unknown
* {_cm_rstripped("1.1.0-rc.1")}
## v1.0.0 ({today_as_str})
### Feature
* feat: add some more text
### Unknown
* {_cm_rstripped("1.0.0")}
## v1.0.0-rc.1 ({today_as_str})
### Breaking
* feat!: add some more text
### Unknown
* {_cm_rstripped("1.0.0-rc.1")}
## v0.1.1-rc.1 ({today_as_str})
### Fix
* fix: add some more text
### Unknown
* {_cm_rstripped("0.1.1-rc.1")}
## v0.1.0 ({today_as_str})
### Unknown
* {_cm_rstripped("0.1.0")}
* Initial commit
"""


def test_default_changelog_template(
    repo_with_git_flow_and_release_channels_angular_commits, default_angular_parser
):
    repo = repo_with_git_flow_and_release_channels_angular_commits
    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    rh = ReleaseHistory.from_git_history(
        repo=repo, translator=VersionTranslator(), commit_parser=default_angular_parser
    )
    context = make_changelog_context(
        hvcs_client=Github(remote_url=repo.remote().url), release_history=rh
    )
    context.bind_to_environment(env)
    actual_content = env.from_string(default_changelog_template).render()
    assert actual_content == EXPECTED_CONTENT


def test_default_changelog_template_using_tag_format(
    repo_with_git_flow_and_release_channels_angular_commits_using_tag_format,
    default_angular_parser,
):
    repo = repo_with_git_flow_and_release_channels_angular_commits_using_tag_format
    env = environment(trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    rh = ReleaseHistory.from_git_history(
        repo=repo,
        translator=VersionTranslator(tag_format="vpy{version}"),
        commit_parser=default_angular_parser,
    )
    context = make_changelog_context(
        hvcs_client=Github(remote_url=repo.remote().url), release_history=rh
    )
    context.bind_to_environment(env)

    actual_content = env.from_string(default_changelog_template).render()
    assert actual_content == EXPECTED_CONTENT
