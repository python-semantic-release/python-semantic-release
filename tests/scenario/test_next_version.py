import pytest
from pytest import lazy_fixture
# Limitation in pytest-lazy-fixture - see https://stackoverflow.com/a/69884019
# from pytest_lazyfixture import lazy_fixture

from semantic_release.version.translator import VersionTranslator
from semantic_release.version.version import Version
from semantic_release.version.algorithm import next_version
from tests.const import (
    ANGULAR_COMMITS_PATCH,
    ANGULAR_COMMITS_MINOR,
    ANGULAR_COMMITS_MAJOR,

    EMOJI_COMMITS_PATCH,
    EMOJI_COMMITS_MINOR,
    EMOJI_COMMITS_MAJOR,

    TAG_COMMITS_PATCH,
    TAG_COMMITS_MINOR,
    TAG_COMMITS_MAJOR
)
from tests.helper import add_text_to_file


# TODO: it'd be nice to not hard-code the versions into
# this testing

@pytest.mark.parametrize(
    "repo, commit_parser, commit_messages, translator, prerelease, expected_new_version",
    [
        # ANGULAR parser
        # Latest version for repo_with_no_tags is currently 0.0.0 (default)
        # It's biggest change type is minor, so the next version should be 0.1.0
        (lazy_fixture("repo_with_no_tags_angular_commits"), lazy_fixture("default_angular_parser"), [],                    VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_angular_commits"), lazy_fixture("default_angular_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),

        # Latest version for repo_with_single_branch is currently 0.1.1
        # Note repo_with_single_branch isn't modelled with prereleases
        (lazy_fixture("repo_with_single_branch_angular_commits"), lazy_fixture("default_angular_parser"), [],                    VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_angular_commits"), lazy_fixture("default_angular_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH, VersionTranslator(), False, "0.1.2"),
        (lazy_fixture("repo_with_single_branch_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR, VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_angular_commits"), lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),

        # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),[],                     VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),[],                     VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),["uninteresting"],      VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),["uninteresting"],      VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_PATCH,  VersionTranslator(), False, "0.2.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_PATCH,  VersionTranslator(), True,  "0.2.1-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
        # The last full release version was 0.2.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), [],                     VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), [],                     VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ["uninteresting"],      VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ["uninteresting"],      VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
        # The last full release version was 1.1.1, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), [],                     VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), [],                     VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ["uninteresting"],      VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ["uninteresting"],      VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_PATCH,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MINOR,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR,  VersionTranslator(), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_angular_commits"),lazy_fixture("default_angular_parser"), ANGULAR_COMMITS_MAJOR,  VersionTranslator(), True,  "2.0.0-rc.1"),

        # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
        # The last full release version was 1.0.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),[],                     VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),[],                     VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_angular_commits"),lazy_fixture("default_angular_parser"),ANGULAR_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), True,  "2.0.0-alpha.1"),


        # EMOJI parser
        # Latest version for repo_with_no_tags is currently 0.0.0 (default)
        # It's biggest change type is minor, so the next version should be 0.1.0
        (lazy_fixture("repo_with_no_tags_emoji_commits"), lazy_fixture("default_emoji_parser"), [],                    VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_emoji_commits"), lazy_fixture("default_emoji_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),
        # Latest version for repo_with_single_branch is currently 0.1.1
        # Note repo_with_single_branch isn't modelled with prereleases
        (lazy_fixture("repo_with_single_branch_emoji_commits"), lazy_fixture("default_emoji_parser"), [],                    VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_emoji_commits"), lazy_fixture("default_emoji_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH, VersionTranslator(), False, "0.1.2"),
        (lazy_fixture("repo_with_single_branch_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR, VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_emoji_commits"), lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),

        # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),[],                     VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),[],                     VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),["uninteresting"],      VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),["uninteresting"],      VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_PATCH,  VersionTranslator(), False, "0.2.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_PATCH,  VersionTranslator(), True,  "0.2.1-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
        # The last full release version was 0.2.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), [],                     VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), [],                     VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), ["uninteresting"],      VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), ["uninteresting"],      VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
        # The last full release version was 1.1.1, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), [],                     VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), [],                     VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), ["uninteresting"],      VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), ["uninteresting"],      VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_PATCH,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MINOR,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR,  VersionTranslator(), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_emoji_commits"),lazy_fixture("default_emoji_parser"), EMOJI_COMMITS_MAJOR,  VersionTranslator(), True,  "2.0.0-rc.1"),

        # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
        # The last full release version was 1.0.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),[],                     VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),[],                     VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_emoji_commits"),lazy_fixture("default_emoji_parser"),EMOJI_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), True,  "2.0.0-alpha.1"),

        # SCIPY parser
        # Latest version for repo_with_no_tags is currently 0.0.0 (default)
        # It's biggest change type is minor, so the next version should be 0.1.0
        (lazy_fixture("repo_with_no_tags_scipy_commits"), lazy_fixture("default_scipy_parser"), [],                    VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_scipy_commits"), lazy_fixture("default_scipy_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"), VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"), VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"), VersionTranslator(), False, "1.0.0"),
        # Latest version for repo_with_single_branch is currently 0.1.1
        # Note repo_with_single_branch isn't modelled with prereleases
        (lazy_fixture("repo_with_single_branch_scipy_commits"), lazy_fixture("default_scipy_parser"), [],                    VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_scipy_commits"), lazy_fixture("default_scipy_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"), VersionTranslator(), False, "0.1.2"),
        (lazy_fixture("repo_with_single_branch_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"), VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_scipy_commits"), lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"), VersionTranslator(), False, "1.0.0"),

        # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),[],                     VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),[],                     VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),["uninteresting"],      VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),["uninteresting"],      VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_patch"),  VersionTranslator(), False, "0.2.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_patch"),  VersionTranslator(), True,  "0.2.1-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_minor"),  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_minor"),  VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_major"),  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_major"),  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
        # The last full release version was 0.2.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), [],                     VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), [],                     VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), ["uninteresting"],      VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), ["uninteresting"],      VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"),  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"),  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"),  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"),  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"),  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"),  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
        # The last full release version was 1.1.1, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), [],                     VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), [],                     VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), ["uninteresting"],      VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), ["uninteresting"],      VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"),  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_patch"),  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"),  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_minor"),  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"),  VersionTranslator(), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_scipy_commits"),lazy_fixture("default_scipy_parser"), lazy_fixture("scipy_commits_major"),  VersionTranslator(), True,  "2.0.0-rc.1"),

        # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
        # The last full release version was 1.0.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),[],                     VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),[],                     VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_patch"),  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_patch"),  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_minor"),  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_minor"),  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_major"),  VersionTranslator(prerelease_token="alpha"), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_scipy_commits"),lazy_fixture("default_scipy_parser"),lazy_fixture("scipy_commits_major"),  VersionTranslator(prerelease_token="alpha"), True,  "2.0.0-alpha.1"),

        # TAG parser
        # Latest version for repo_with_no_tags is currently 0.0.0 (default)
        # It's biggest change type is minor, so the next version should be 0.1.0
        (lazy_fixture("repo_with_no_tags_tag_commits"), lazy_fixture("default_tag_parser"), [],                    VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_tag_commits"), lazy_fixture("default_tag_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR, VersionTranslator(), False, "0.1.0"),
        (lazy_fixture("repo_with_no_tags_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),
        # Latest version for repo_with_single_branch is currently 0.1.1
        # Note repo_with_single_branch isn't modelled with prereleases
        (lazy_fixture("repo_with_single_branch_tag_commits"), lazy_fixture("default_tag_parser"), [],                    VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_tag_commits"), lazy_fixture("default_tag_parser"), ["uninteresting"],     VersionTranslator(), False, "0.1.1"),
        (lazy_fixture("repo_with_single_branch_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH, VersionTranslator(), False, "0.1.2"),
        (lazy_fixture("repo_with_single_branch_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR, VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_tag_commits"), lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR, VersionTranslator(), False, "1.0.0"),

        # Latest version for repo_with_single_branch_and_prereleases is currently 0.2.0
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),[],                     VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),[],                     VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),["uninteresting"],      VersionTranslator(), False, "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),["uninteresting"],      VersionTranslator(), True,  "0.2.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_PATCH,  VersionTranslator(), False, "0.2.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_PATCH,  VersionTranslator(), True,  "0.2.1-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_single_branch_and_prereleases_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_main_and_feature_branches is currently 0.3.0-rc.1.
        # The last full release version was 0.2.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), [],                     VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), [],                     VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), ["uninteresting"],      VersionTranslator(), False, "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), ["uninteresting"],      VersionTranslator(), True,  "0.3.0-rc.1"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR,  VersionTranslator(), False, "0.3.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR,  VersionTranslator(), True,  "0.3.0-rc.2"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR,  VersionTranslator(), False, "1.0.0"),
        (lazy_fixture("repo_with_main_and_feature_branches_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR,  VersionTranslator(), True,  "1.0.0-rc.1"),

        # Latest version for repo_with_git_flow is currently 1.2.0-rc.2
        # The last full release version was 1.1.1, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), [],                     VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), [],                     VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), ["uninteresting"],      VersionTranslator(), False, "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), ["uninteresting"],      VersionTranslator(), True,  "1.2.0-rc.2"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_PATCH,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR,  VersionTranslator(), False, "1.2.0"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MINOR,  VersionTranslator(), True,  "1.2.0-rc.3"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR,  VersionTranslator(), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_tag_commits"),lazy_fixture("default_tag_parser"), TAG_COMMITS_MAJOR,  VersionTranslator(), True,  "2.0.0-rc.1"),

        # Latest version for repo_with_git_flow_and_release_channels is currently 1.1.0-alpha.3
        # The last full release version was 1.0.0, so it's had a minor prerelease
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),[],                     VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),[],                     VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), False, "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),["uninteresting"],      VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.3"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_PATCH,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), False, "1.1.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MINOR,  VersionTranslator(prerelease_token="alpha"), True,  "1.1.0-alpha.4"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), False, "2.0.0"),
        (lazy_fixture("repo_with_git_flow_and_release_channels_tag_commits"),lazy_fixture("default_tag_parser"),TAG_COMMITS_MAJOR,  VersionTranslator(prerelease_token="alpha"), True,  "2.0.0-alpha.1"),
    ],
)
def test_algorithm(
    repo,
    file_in_repo,
    commit_parser,
    commit_messages,
    translator,
    prerelease,
    expected_new_version,
):
    for commit_message in commit_messages:
        add_text_to_file(repo, file_in_repo)
        repo.git.commit(m=commit_message)

    new_version = next_version(repo, translator, commit_parser, prerelease)

    assert new_version == Version.parse(expected_new_version, prerelease_token=translator.prerelease_token)
