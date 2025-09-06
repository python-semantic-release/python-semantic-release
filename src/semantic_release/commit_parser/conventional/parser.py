from __future__ import annotations

from functools import reduce
from logging import getLogger
from re import (
    DOTALL,
    IGNORECASE,
    MULTILINE,
    Match as RegexMatch,
    Pattern,
    compile as regexp,
    error as RegexError,  # noqa: N812
)
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from git.objects.commit import Commit

from semantic_release.commit_parser._base import CommitParser
from semantic_release.commit_parser.conventional.options import (
    ConventionalCommitParserOptions,
)
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

if TYPE_CHECKING:
    pass


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


class ConventionalCommitParser(
    CommitParser[ParseResult, ConventionalCommitParserOptions]
):
    """
    A commit parser for projects conforming to the conventional commits specification.

    See https://www.conventionalcommits.org/en/v1.0.0/
    """

    # TODO: Deprecate in lieu of get_default_options()
    parser_options = ConventionalCommitParserOptions

    # GitHub & Gitea use (#123), GitLab uses (!123), and BitBucket uses (pull request #123)
    mr_selector = regexp(r"[\t ]+\((?:pull request )?(?P<mr_number>[#!]\d+)\)[\t ]*$")

    issue_selector = regexp(
        str.join(
            "",
            [
                r"^(?:clos(?:e|es|ed|ing)|fix(?:es|ed|ing)?|resolv(?:e|es|ed|ing)|implement(?:s|ed|ing)?):",
                r"[\t ]+(?P<issue_predicate>.+)[\t ]*$",
            ],
        ),
        flags=MULTILINE | IGNORECASE,
    )

    notice_selector = regexp(r"^NOTICE: (?P<notice>.+)$")

    common_commit_msg_filters: ClassVar[dict[str, tuple[Pattern[str], str]]] = {
        "typo-extra-spaces": (regexp(r"(\S)  +(\S)"), r"\1 \2"),
        "git-header-commit": (
            regexp(r"^[\t ]*commit [0-9a-f]+$\n?", flags=MULTILINE),
            "",
        ),
        "git-header-author": (
            regexp(r"^[\t ]*Author: .+$\n?", flags=MULTILINE),
            "",
        ),
        "git-header-date": (
            regexp(r"^[\t ]*Date: .+$\n?", flags=MULTILINE),
            "",
        ),
        "git-squash-heading": (
            regexp(
                r"^[\t ]*Squashed commit of the following:.*$\n?",
                flags=MULTILINE,
            ),
            "",
        ),
    }

    def __init__(self, options: ConventionalCommitParserOptions | None = None) -> None:
        super().__init__(options)

        self._logger = getLogger(
            str.join(".", [self.__module__, self.__class__.__name__])
        )

        try:
            commit_type_pattern = regexp(
                r"(?P<type>%s)" % str.join("|", self.options.allowed_tags)
            )
        except RegexError as err:
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

        self.commit_subject = regexp(
            str.join(
                "",
                [
                    f"^{commit_type_pattern.pattern}",
                    r"(?:\((?P<scope>[^\n]+)\))?",
                    r"(?P<break>!)?:\s+",
                    r"(?P<subject>[^\n]+)",
                ],
            )
        )

        self.commit_msg_pattern = regexp(
            str.join(
                "",
                [
                    self.commit_subject.pattern,
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=DOTALL,
        )

        self.filters: dict[str, tuple[Pattern[str], str]] = {
            **self.common_commit_msg_filters,
            "git-squash-commit-prefix": (
                regexp(
                    str.join(
                        "",
                        [
                            r"^(?:[\t ]*[*-][\t ]+|[\t ]+)?",  # bullet points or indentation
                            commit_type_pattern.pattern + r"\b",  # prior to commit type
                        ],
                    ),
                    flags=MULTILINE,
                ),
                # move commit type to the start of the line
                r"\1",
            ),
        }

    def get_default_options(self) -> ConventionalCommitParserOptions:
        return ConventionalCommitParserOptions()

    def log_parse_error(self, commit: Commit, error: str) -> ParseError:
        self._logger.debug(error)
        return ParseError(commit, error=error)

    def commit_body_components_separator(
        self, accumulator: dict[str, list[str]], text: str
    ) -> dict[str, list[str]]:
        if (match := breaking_re.match(text)) and (brk_desc := match.group(1)):
            accumulator["breaking_descriptions"].append(brk_desc)
            return accumulator

        if (match := self.notice_selector.match(text)) and (
            notice := match.group("notice")
        ):
            accumulator["notices"].append(notice)
            return accumulator

        if match := self.issue_selector.search(text):
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
                return accumulator

        # Prevent appending duplicate descriptions
        if text not in accumulator["descriptions"]:
            accumulator["descriptions"].append(text)

        return accumulator

    def parse_message(self, message: str) -> ParsedMessageResult | None:
        return (
            self.create_parsed_message_result(match)
            if (match := self.commit_msg_pattern.match(message))
            else None
        )

    def create_parsed_message_result(
        self, match: RegexMatch[str]
    ) -> ParsedMessageResult:
        parsed_break = match.group("break")
        parsed_scope = match.group("scope") or ""
        parsed_subject = match.group("subject")
        parsed_text = match.group("text")
        parsed_type = match.group("type")

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(parsed_subject):
            linked_merge_request = mr_match.group("mr_number")
            parsed_subject = self.mr_selector.sub("", parsed_subject).strip()

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
            return self.log_parse_error(
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
            return self.log_parse_error(
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

            # Check if the paragraph is the start of a new conventional commit
            # Note: that we check that the subject has more than one word to differentiate from
            # a closing footer (e.g. "fix: #123", or "fix: ABC-123")
            if (match := self.commit_subject.search(clean_paragraph)) and len(
                match.group("subject").split(" ")
            ) > 1:
                # Since we found the start of the new commit, store any previous commit
                # message separately and start the new commit message
                if current_msg:
                    separate_commit_msgs.append(current_msg)

                current_msg = clean_paragraph
                continue

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

        return [*separate_commit_msgs, current_msg]
