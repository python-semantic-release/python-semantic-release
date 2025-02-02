"""
Angular commit style parser
https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines
"""

from __future__ import annotations

import logging
import re
from functools import reduce
from itertools import zip_longest
from re import compile as regexp
from textwrap import dedent
from typing import TYPE_CHECKING, Tuple

from git.objects.commit import Commit
from pydantic.dataclasses import dataclass

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import (
    breaking_re,
    deep_copy_commit,
    force_str,
    parse_paragraphs,
)
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidParserOptions
from semantic_release.helpers import sort_numerically, text_reducer

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit


logger = logging.getLogger(__name__)


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    logger.debug(error)
    return ParseError(commit, error=error)


# TODO: Remove from here, allow for user customization instead via options
# types with long names in changelog
LONG_TYPE_NAMES = {
    "build": "build system",
    "ci": "continuous integration",
    "chore": "chores",
    "docs": "documentation",
    "feat": "features",
    "fix": "bug fixes",
    "perf": "performance improvements",
    "refactor": "refactoring",
    "style": "code style",
    "test": "testing",
}


@dataclass
class AngularParserOptions(ParserOptions):
    """Options dataclass for AngularCommitParser"""

    minor_tags: Tuple[str, ...] = ("feat",)
    """Commit-type prefixes that should result in a minor release bump."""

    patch_tags: Tuple[str, ...] = ("fix", "perf")
    """Commit-type prefixes that should result in a patch release bump."""

    other_allowed_tags: Tuple[str, ...] = (
        "build",
        "chore",
        "ci",
        "docs",
        "style",
        "refactor",
        "test",
    )
    """Commit-type prefixes that are allowed but do not result in a version bump."""

    allowed_tags: Tuple[str, ...] = (
        *minor_tags,
        *patch_tags,
        *other_allowed_tags,
    )
    """
    All commit-type prefixes that are allowed.

    These are used to identify a valid commit message. If a commit message does not start with
    one of these prefixes, it will not be considered a valid commit message.
    """

    default_bump_level: LevelBump = LevelBump.NO_RELEASE
    """The minimum bump level to apply to valid commit message."""

    # TODO: breaking change v10, change default to True
    parse_squash_commits: bool = False
    """Toggle flag for whether or not to parse squash commits"""

    # TODO: breaking change v10, change default to True
    ignore_merge_commits: bool = False
    """Toggle flag for whether or not to ignore merge commits"""

    @property
    def tag_to_level(self) -> dict[str, LevelBump]:
        """A mapping of commit tags to the level bump they should result in."""
        return self._tag_to_level

    def __post_init__(self) -> None:
        self._tag_to_level: dict[str, LevelBump] = {
            str(tag): level
            for tag, level in [
                # we have to do a type ignore as zip_longest provides a type that is not specific enough
                # for our expected output. Due to the empty second array, we know the first is always longest
                # and that means no values in the first entry of the tuples will ever be a LevelBump. We
                # apply a str() to make mypy happy although it will never happen.
                *zip_longest(self.allowed_tags, (), fillvalue=self.default_bump_level),
                *zip_longest(self.patch_tags, (), fillvalue=LevelBump.PATCH),
                *zip_longest(self.minor_tags, (), fillvalue=LevelBump.MINOR),
            ]
            if "|" not in str(tag)
        }


class AngularCommitParser(CommitParser[ParseResult, AngularParserOptions]):
    """
    A commit parser for projects conforming to the angular style of conventional
    commits. See https://www.conventionalcommits.org/en/v1.0.0-beta.4/
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = AngularParserOptions

    def __init__(self, options: AngularParserOptions | None = None) -> None:
        super().__init__(options)

        try:
            commit_type_pattern = regexp(
                r"(?P<type>%s)" % str.join("|", self.options.allowed_tags)
            )
        except re.error as err:
            raise InvalidParserOptions(
                str.join(
                    "\n",
                    [
                        f"Invalid options for {self.__class__.__name__}",
                        "Unable to create regular expression from configured commit-types.",
                        "Please check the configured commit-types and remove or escape any regular expression characters.",
                    ],
                )
            ) from err

        self.commit_prefix = regexp(
            str.join(
                "",
                [
                    f"^{commit_type_pattern.pattern}",
                    r"(?:\((?P<scope>[^\n]+)\))?",
                    # TODO: remove ! support as it is not part of the angular commit spec (its part of conventional commits spec)
                    r"(?P<break>!)?:\s+",
                ],
            )
        )

        self.re_parser = regexp(
            str.join(
                "",
                [
                    self.commit_prefix.pattern,
                    r"(?P<subject>[^\n]+)",
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=re.DOTALL,
        )

        # GitHub & Gitea use (#123), GitLab uses (!123), and BitBucket uses (pull request #123)
        self.mr_selector = regexp(
            r"[\t ]+\((?:pull request )?(?P<mr_number>[#!]\d+)\)[\t ]*$"
        )
        self.issue_selector = regexp(
            str.join(
                "",
                [
                    r"^(?:clos(?:e|es|ed|ing)|fix(?:es|ed|ing)?|resolv(?:e|es|ed|ing)|implement(?:s|ed|ing)?):",
                    r"[\t ]+(?P<issue_predicate>.+)[\t ]*$",
                ],
            ),
            flags=re.MULTILINE | re.IGNORECASE,
        )
        self.notice_selector = regexp(r"^NOTICE: (?P<notice>.+)$")
        self.filters = {
            "typo-extra-spaces": (regexp(r"(\S)  +(\S)"), r"\1 \2"),
            "git-header-commit": (
                regexp(r"^[\t ]*commit [0-9a-f]+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-header-author": (
                regexp(r"^[\t ]*Author: .+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-header-date": (
                regexp(r"^[\t ]*Date: .+$\n?", flags=re.MULTILINE),
                "",
            ),
            "git-squash-heading": (
                regexp(
                    r"^[\t ]*Squashed commit of the following:.*$\n?",
                    flags=re.MULTILINE,
                ),
                "",
            ),
            "git-squash-commit-prefix": (
                regexp(
                    str.join(
                        "",
                        [
                            r"^(?:[\t ]*[*-][\t ]+|[\t ]+)?",  # bullet points or indentation
                            commit_type_pattern.pattern + r"\b",  # prior to commit type
                        ],
                    ),
                    flags=re.MULTILINE,
                ),
                # move commit type to the start of the line
                r"\1",
            ),
        }

    @staticmethod
    def get_default_options() -> AngularParserOptions:
        return AngularParserOptions()

    def commit_body_components_separator(
        self, accumulator: dict[str, list[str]], text: str
    ) -> dict[str, list[str]]:
        if (match := breaking_re.match(text)) and (brk_desc := match.group(1)):
            accumulator["breaking_descriptions"].append(brk_desc)
            # TODO: breaking change v10, removes breaking change footers from descriptions
            # return accumulator

        elif (match := self.notice_selector.match(text)) and (
            notice := match.group("notice")
        ):
            accumulator["notices"].append(notice)
            # TODO: breaking change v10, removes notice footers from descriptions
            # return accumulator

        elif match := self.issue_selector.search(text):
            # if match := self.issue_selector.search(text):
            predicate = regexp(r",? and | *[,;/& ] *").sub(
                ",", match.group("issue_predicate") or ""
            )
            # Almost all issue trackers use a number to reference an issue so
            # we use a simple regexp to validate the existence of a number which helps filter out
            # any non-issue references that don't fit our expected format
            has_number = regexp(r"\d+")
            new_issue_refs: set[str] = set(
                filter(
                    lambda issue_str, validator=has_number: validator.search(issue_str),  # type: ignore[arg-type]
                    predicate.split(","),
                )
            )
            if new_issue_refs:
                accumulator["linked_issues"] = sort_numerically(
                    set(accumulator["linked_issues"]).union(new_issue_refs)
                )
                # TODO: breaking change v10, removes resolution footers from descriptions
                # return accumulator

        # Prevent appending duplicate descriptions
        if text not in accumulator["descriptions"]:
            accumulator["descriptions"].append(text)

        return accumulator

    def parse_message(self, message: str) -> ParsedMessageResult | None:
        if not (parsed := self.re_parser.match(message)):
            return None

        parsed_break = parsed.group("break")
        parsed_scope = parsed.group("scope") or ""
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(parsed_subject):
            linked_merge_request = mr_match.group("mr_number")
            # TODO: breaking change v10, removes PR number from subject/descriptions
            # expects changelog template to format the line accordingly
            # parsed_subject = self.pr_selector.sub("", parsed_subject).strip()

        body_components: dict[str, list[str]] = reduce(
            self.commit_body_components_separator,
            [
                # Insert the subject before the other paragraphs
                parsed_subject,
                *parse_paragraphs(parsed_text or ""),
            ],
            {
                "breaking_descriptions": [],
                "descriptions": [],
                "notices": [],
                "linked_issues": [],
            },
        )

        level_bump = (
            LevelBump.MAJOR
            # TODO: remove parsed break support as it is not part of the angular commit spec (its part of conventional commits spec)
            if body_components["breaking_descriptions"] or parsed_break
            else self.options.tag_to_level.get(
                parsed_type, self.options.default_bump_level
            )
        )

        return ParsedMessageResult(
            bump=level_bump,
            type=parsed_type,
            category=LONG_TYPE_NAMES.get(parsed_type, parsed_type),
            scope=parsed_scope,
            descriptions=tuple(body_components["descriptions"]),
            breaking_descriptions=tuple(body_components["breaking_descriptions"]),
            release_notices=tuple(body_components["notices"]),
            linked_issues=tuple(body_components["linked_issues"]),
            linked_merge_request=linked_merge_request,
        )

    @staticmethod
    def is_merge_commit(commit: Commit) -> bool:
        return len(commit.parents) > 1

    def parse_commit(self, commit: Commit) -> ParseResult:
        if not (parsed_msg_result := self.parse_message(force_str(commit.message))):
            return _logged_parse_error(
                commit,
                f"Unable to parse commit message: {commit.message!r}",
            )

        return ParsedCommit.from_parsed_message_result(commit, parsed_msg_result)

    # Maybe this can be cached as an optimization, similar to how
    # mypy/pytest use their own caching directories, for very large commit
    # histories?
    # The problem is the cache likely won't be present in CI environments
    def parse(self, commit: Commit) -> ParseResult | list[ParseResult]:
        """
        Parse a commit message

        If the commit message is a squashed merge commit, it will be split into
        multiple commits, each of which will be parsed separately. Single commits
        will be returned as a list of a single ParseResult.
        """
        if self.options.ignore_merge_commits and self.is_merge_commit(commit):
            return _logged_parse_error(
                commit, "Ignoring merge commit: %s" % commit.hexsha[:8]
            )

        separate_commits: list[Commit] = (
            self.unsquash_commit(commit)
            if self.options.parse_squash_commits
            else [commit]
        )

        # Parse each commit individually if there were more than one
        parsed_commits: list[ParseResult] = list(
            map(self.parse_commit, separate_commits)
        )

        def add_linked_merge_request(
            parsed_result: ParseResult, mr_number: str
        ) -> ParseResult:
            return (
                parsed_result
                if not isinstance(parsed_result, ParsedCommit)
                else ParsedCommit(
                    **{
                        **parsed_result._asdict(),
                        "linked_merge_request": mr_number,
                    }
                )
            )

        # TODO: improve this for other VCS systems other than GitHub & BitBucket
        # Github works as the first commit in a squash merge commit has the PR number
        # appended to the first line of the commit message
        lead_commit = next(iter(parsed_commits))

        if isinstance(lead_commit, ParsedCommit) and lead_commit.linked_merge_request:
            # If the first commit has linked merge requests, assume all commits
            # are part of the same PR and add the linked merge requests to all
            # parsed commits
            parsed_commits = [
                lead_commit,
                *map(
                    lambda parsed_result, mr=lead_commit.linked_merge_request: (  # type: ignore[misc]
                        add_linked_merge_request(parsed_result, mr)
                    ),
                    parsed_commits[1:],
                ),
            ]

        elif isinstance(lead_commit, ParseError) and (
            mr_match := self.mr_selector.search(force_str(lead_commit.message))
        ):
            # Handle BitBucket Squash Merge Commits (see #1085), which have non angular commit
            # format but include the PR number in the commit subject that we want to extract
            linked_merge_request = mr_match.group("mr_number")

            # apply the linked MR to all commits
            parsed_commits = [
                add_linked_merge_request(parsed_result, linked_merge_request)
                for parsed_result in parsed_commits
            ]

        return parsed_commits

    def unsquash_commit(self, commit: Commit) -> list[Commit]:
        # GitHub EXAMPLE:
        # feat(changelog): add autofit_text_width filter to template environment (#1062)
        #
        # This change adds an equivalent style formatter that can apply a text alignment
        # to a maximum width and also maintain an indent over paragraphs of text
        #
        # * docs(changelog-templates): add definition & usage of autofit_text_width template filter
        #
        # * test(changelog-context): add test cases to check autofit_text_width filter use
        #
        # `git merge --squash` EXAMPLE:
        # Squashed commit of the following:
        #
        # commit 63ec09b9e844e616dcaa7bae35a0b66671b59fbb
        # Author: codejedi365 <codejedi365@gmail.com>
        # Date:   Sun Oct 13 12:05:23 2024 -0600
        #
        #     feat(release-config): some commit subject
        #

        # Return a list of artificial commits (each with a single commit message)
        return [
            # create a artificial commit object (copy of original but with modified message)
            Commit(
                **{
                    **deep_copy_commit(commit),
                    "message": commit_msg,
                }
            )
            for commit_msg in self.unsquash_commit_message(force_str(commit.message))
        ] or [commit]

    def unsquash_commit_message(self, message: str) -> list[str]:
        normalized_message = message.replace("\r", "").strip()

        # split by obvious separate commits (applies to manual git squash merges)
        obvious_squashed_commits = self.filters["git-header-commit"][0].split(
            normalized_message
        )

        separate_commit_msgs: list[str] = reduce(
            lambda all_msgs, msgs: all_msgs + msgs,
            map(self._find_squashed_commits_in_str, obvious_squashed_commits),
            [],
        )

        return list(filter(None, separate_commit_msgs))

    def _find_squashed_commits_in_str(self, message: str) -> list[str]:
        separate_commit_msgs: list[str] = []
        current_msg = ""

        for paragraph in filter(None, message.strip().split("\n\n")):
            # Apply filters to normalize the paragraph
            clean_paragraph = reduce(text_reducer, self.filters.values(), paragraph)

            # remove any filtered (and now empty) paragraphs (ie. the git headers)
            if not clean_paragraph.strip():
                continue

            # Check if the paragraph is the start of a new angular commit
            if not self.commit_prefix.search(clean_paragraph):
                if not separate_commit_msgs and not current_msg:
                    # if there are no separate commit messages and no current message
                    # then this is the first commit message
                    current_msg = dedent(clean_paragraph)
                    continue

                # append the paragraph as part of the previous commit message
                if current_msg:
                    current_msg += f"\n\n{dedent(clean_paragraph)}"
                # else: drop the paragraph
                continue

            # Since we found the start of the new commit, store any previous commit
            # message separately and start the new commit message
            if current_msg:
                separate_commit_msgs.append(current_msg)

            current_msg = clean_paragraph

        return [*separate_commit_msgs, current_msg]
