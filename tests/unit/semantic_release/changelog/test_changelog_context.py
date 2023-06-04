import pytest
from git.objects.base import Object
from pytest_lazyfixture import lazy_fixture

from semantic_release.changelog import environment, make_changelog_context
from semantic_release.changelog.release_history import ReleaseHistory
from semantic_release.hvcs import Gitea, Github, Gitlab
from semantic_release.version.translator import VersionTranslator

NULL_HEX_SHA = Object.NULL_HEX_SHA
SHORT_SHA = NULL_HEX_SHA[:7]


# Test with just one project for the moment - can be expanded to all
# example projects later

CHANGELOG_TEMPLATE = r"""
# CHANGELOG
{% if context.history.unreleased | length > 0 %}
## Unreleased
{% for type_, commits in context.history.unreleased.items() %}
### {{ type_ | capitalize }}
{% for commit in commits %}{% if type_ != "unknown" %}
* {{ commit.message.rstrip() }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{% else %}
* {{ commit.message.rstrip() }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{% endif %}{% endfor %}{% endfor %}{% endif %}
{% for version, release in context.history.released.items() %}
## {{ version.as_tag() }} ({{ release.tagged_date.strftime("%Y-%m-%d") }})
{% for type_, commits in release["elements"].items() %}
### {{ type_ | capitalize }}
{% for commit in commits %}{% if type_ != "unknown" %}
* {{ commit.message.rstrip() }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{% else %}
* {{ commit.message.rstrip() }} ([`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }}))
{% endif %}{% endfor %}{% endfor %}{% endfor %}
"""

EXPECTED_CHANGELOG_CONTENT_ANGULAR = r"""
# CHANGELOG
## v0.2.0
### Feature
* feat: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.2.0-rc.1
### Feature
* feat: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.1-rc.1
### Fix
* fix: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.0
### Unknown
* Initial commit ([`{SHORT_SHA}`]({commit_url}))
"""


EXPECTED_CHANGELOG_CONTENT_EMOJI = r"""
# CHANGELOG
## v0.2.0
### :sparkles:
* :sparkles: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.2.0-rc.1
### :sparkles:
* :sparkles: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.1-rc.1
### :bug:
* :bug: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.0
### Unknown
* Initial commit ([`{SHORT_SHA}`]({commit_url}))
"""

EXPECTED_CHANGELOG_CONTENT_SCIPY = r"""
# CHANGELOG
## v0.2.0
### ENH:
* ENH: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.2.0-rc.1
### ENH:
* ENH: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.1-rc.1
### MAINT:
* MAINT: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.0
### Unknown
* Initial commit ([`{SHORT_SHA}`]({commit_url}))
"""

EXPECTED_CHANGELOG_CONTENT_TAG = r"""
# CHANGELOG
## v0.2.0
### :sparkles:
* :sparkles: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.2.0-rc.1
### :sparkles:
* :sparkles: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.1-rc.1
### :nut_and_bolt:
* :nut_and_bolt: add some more text ([`{SHORT_SHA}`]({commit_url}))
## v0.1.0
### Unknown
* Initial commit ([`{SHORT_SHA}`]({commit_url}))
"""


@pytest.mark.parametrize("changelog_template", (CHANGELOG_TEMPLATE,))
@pytest.mark.parametrize(
    "repo, commit_parser, expected_changelog",
    [
        (
            lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),
            lazy_fixture("default_angular_parser"),
            EXPECTED_CHANGELOG_CONTENT_ANGULAR,
        ),
        (
            lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),
            lazy_fixture("default_emoji_parser"),
            EXPECTED_CHANGELOG_CONTENT_EMOJI,
        ),
        (
            lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),
            lazy_fixture("default_scipy_parser"),
            EXPECTED_CHANGELOG_CONTENT_SCIPY,
        ),
        (
            lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),
            lazy_fixture("default_tag_parser"),
            EXPECTED_CHANGELOG_CONTENT_TAG,
        ),
    ],
)
@pytest.mark.parametrize("hvcs_client_class", (Github, Gitlab, Gitea))
def test_changelog_context(
    repo, changelog_template, commit_parser, expected_changelog, hvcs_client_class
):
    # NOTE: this test only checks that the changelog can be rendered with the
    # contextual information we claim to offer. Testing that templates render
    # appropriately is the responsibility of the template engine's authors,
    # so we shouldn't be re-testing that here.
    hvcs_client = hvcs_client_class(remote_url=repo.remote().url)
    env = environment(lstrip_blocks=True, keep_trailing_newline=True, trim_blocks=True)
    rh = ReleaseHistory.from_git_history(repo, VersionTranslator(), commit_parser)
    context = make_changelog_context(hvcs_client=hvcs_client, release_history=rh)
    context.bind_to_environment(env)
    actual_content = env.from_string(changelog_template).render()
    assert actual_content
