"""Logs
"""
import logging
from typing import Optional

from ..errors import UnknownCommitMessageStyleError
from ..helpers import LoggedFunction
from ..settings import config, current_commit_parser
from ..vcs_helpers import get_commit_log, get_repository_owner_and_name
from .parser_helpers import re_breaking

logger = logging.getLogger(__name__)

LEVELS = {
    1: "patch",
    2: "minor",
    3: "major",
}


@LoggedFunction(logger)
def evaluate_version_bump(current_version: str, force: str = None) -> Optional[str]:
    """
    Read git log since the last release to decide if we should make a major, minor or patch release.

    :param current_version: A string with the current version number.
    :param force: A string with the bump level that should be forced.
    :return: A string with either major, minor or patch if there should be a release.
             If no release is necessary, None will be returned.
    """
    if force:
        return force

    bump = None

    changes = []
    commit_count = 0

    for _hash, commit_message in get_commit_log("v{0}".format(current_version)):
        if commit_message.startswith(current_version):
            # Stop once we reach the current version
            # (we are looping in the order of newest -> oldest)
            logger.debug(
                '"{}" is commit for {}, breaking loop'.format(
                    commit_message, current_version
                )
            )
            break

        commit_count += 1

        # Attempt to parse this commit using the currently-configured parser
        try:
            message = current_commit_parser()(commit_message)
            changes.append(message.bump)
        except UnknownCommitMessageStyleError as err:
            logger.debug(f"Ignoring UnknownCommitMessageStyleError: {err}")
            pass

    logger.debug(f"Commits found since last release: {commit_count}")

    if changes:
        # Select the largest required bump level from the commits we parsed
        level = max(changes)
        if level in LEVELS:
            bump = LEVELS[level]
        else:
            logger.warning(f"Unknown bump level {level}")

    if (
        config.getboolean("semantic_release", "patch_without_tag")
        and commit_count > 0
        and bump is None
    ):
        bump = "patch"
        logger.debug(f"Changing bump level to patch based on config patch_without_tag")

    return bump


@LoggedFunction(logger)
def generate_changelog(from_version: str, to_version: str = None) -> dict:
    """
    Parse a changelog dictionary for the given version.

    :param from_version: The version before where the changelog starts.
                         The changelog will be generated from the commit after this one.
    :param to_version: The last version included in the changelog.
    :return: A dict with changelog sections and commits
    """
    changes: dict = {
        "feature": [],
        "fix": [],
        "documentation": [],
        "refactor": [],
        "breaking": [],
        "performance": [],
    }

    rev = None
    if from_version:
        rev = "v{0}".format(from_version)

    found_the_release = to_version is None
    for _hash, commit_message in get_commit_log(rev):
        if not found_the_release:
            # Skip until we find the last commit in this release
            # (we are looping in the order of newest -> oldest)
            if to_version and to_version not in commit_message:
                continue
            else:
                logger.debug(
                    f"Reached the start of {to_version}, beginning changelog generation"
                )
                found_the_release = True

        if from_version is not None and from_version in commit_message:
            # We reached the previous release
            logger.debug(f"{from_version} reached, ending changelog generation")
            break

        try:
            message = current_commit_parser()(commit_message)
            if message.type not in changes:
                logger.debug(f"Excluding commit type {message.type} from changelog")
                continue

            # Capialize the first letter of the message, leaving others as they were
            # (using str.capitalize() would make the other letters lowercase)
            capital_message = (
                message.descriptions[0][0].upper() + message.descriptions[0][1:]
            )
            changes[message.type].append((_hash, capital_message))

            # Handle breaking change message
            parts = None
            if message.bump == 3 and len(message.descriptions) > 1:
                # Check each paragraph for breaking changes
                # This can pick up multiple paragraphs, e.g. in squashed commits
                breaking_paragraphs = list()
                for paragraph in message.descriptions[1:]:
                    parts = re_breaking.match(paragraph)
                    if parts:
                        # This paragraph describes a breaking change
                        breaking_paragraphs.append(parts.group(1))

                if len(breaking_paragraphs) > 0:
                    # Use selected paragraphs
                    for paragraph in breaking_paragraphs:
                        changes["breaking"].append((_hash, paragraph))
                else:
                    # No paragraphs begin with "BREAKING CHANGE:"
                    # Use the subject instead
                    changes["breaking"].append((_hash, message.descriptions[0]))

        except UnknownCommitMessageStyleError as err:
            logger.debug(f"Ignoring UnknownCommitMessageStyleError: {err}")
            pass

    return changes


def get_github_compare_url(from_version: str, to_version: str) -> str:
    """
    Get the GitHub comparison link between two version tags.

    :param from_version: The older version to compare.
    :param to_version: The newer version to compare.
    :return: Link to view a comparison between the two versions.
    """
    owner, name = get_repository_owner_and_name()
    return (
        f"https://github.com/{owner}/{name}"
        f"/compare/v{from_version}...v{to_version}"
    )


@LoggedFunction(logger)
def markdown_changelog(version: str, changelog: dict, header: bool = False, previous_version: str = None) -> str:
    """
    Generate a markdown version of the changelog.

    :param version: A string with the version number.
    :param previous_version: A string with the last version number, to
        use for the comparison URL. If omitted, the URL will not be included.
    :param changelog: A parsed changelog dict from generate_changelog.
    :param header: A boolean that decides whether a version number header should be included.
    :return: The markdown formatted changelog.
    """
    output = ""
    if header:
        # Add a heading with the version number
        output += "## v{0}\n".format(version)

    if (
        config.getboolean("semantic_release", "compare_link")
        and config.get("semantic_release", "hvcs").lower() == 'github'
        and previous_version
    ):
        compare_url = get_github_compare_url(previous_version, version)
        output += f"**[See all commits in this version]({compare_url})**\n"

    # Sections which will be shown in the Markdown changelog.
    # This is NOT related to supported commit types.
    changelog_sections = config.get("semantic_release", "changelog_sections")
    changelog_sections = [s.strip() for s in changelog_sections.split(",")]

    for section in changelog_sections:
        if section not in changelog or not changelog[section]:
            # This section does not have any commits
            logger.debug(
                f"Excluding section {section} from markdown changelog because it is empty"
            )
            continue

        # Add a header for the section
        output += "\n### {0}\n".format(section.capitalize())
        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            output += "* {0} ({1})\n".format(item[1], item[0])

    return output
