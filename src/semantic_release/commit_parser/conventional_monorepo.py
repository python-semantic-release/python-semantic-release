from __future__ import annotations

import logging
import os
import re
from fnmatch import fnmatch
from functools import reduce
from itertools import zip_longest
from pathlib import Path
from re import compile as regexp
from typing import TYPE_CHECKING, Any, Iterable

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
from typing_extensions import Annotated

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.angular import LONG_TYPE_NAMES
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import (
    breaking_re,
    parse_paragraphs,
    sort_numerically,
)
from semantic_release.enums import LevelBump
from semantic_release.errors import InvalidParserOptions

if TYPE_CHECKING:  # pragma: no cover
    from git.objects.commit import Commit


logger = logging.getLogger(__name__)


def _logged_parse_error(commit: Commit, error: str) -> ParseError:
    logger.debug(error)
    return ParseError(commit, error=error)


@dataclass
class ConventionalMonorepoParserOptions(ParserOptions):
    """Options dataclass for ConventionalCommitMonorepoParser."""

    minor_tags: tuple[str, ...] = ("feat",)
    """Commit-type prefixes that should result in a minor release bump."""

    patch_tags: tuple[str, ...] = ("fix", "perf")
    """Commit-type prefixes that should result in a patch release bump."""

    other_allowed_tags: tuple[str, ...] = (
        "build",
        "chore",
        "ci",
        "docs",
        "style",
        "refactor",
        "test",
    )
    """Commit-type prefixes that are allowed but do not result in a version bump."""

    default_bump_level: LevelBump = LevelBump.NO_RELEASE
    """The minimum bump level to apply to valid commit message."""

    path_filters: Annotated[tuple[Path, ...], Field(validate_default=True)] = (
        Path("."),
    )
    """
    A set of relative paths to filter commits by. Only commits with file changes that
    match these file paths or its subdirectories will be considered valid commits.

    Syntax is similar to .gitignore with file path globs and inverse file match globs
    via `!` prefix. Paths should be relative to the current working directory.
    """

    scope_prefix: str = ""
    """
    A prefix that will be striped from the scope when parsing commit messages.

    If set, it will cause unscoped commits to be ignored. Use this in tandem with
    the `path_filters` option to filter commits by directory and scope.
    """

    @field_validator("path_filters", mode="before")
    @classmethod
    def convert_strs_to_paths(cls, value: Any) -> tuple[Path]:
        values = value if isinstance(value, Iterable) else [value]
        results = []

        for val in values:
            if isinstance(val, (str, Path)):
                results.append(Path(val))
                continue

            raise TypeError(f"Invalid type: {type(val)}, expected str or Path.")

        return tuple(results)

    @field_validator("path_filters", mode="after")
    @classmethod
    def resolve_path(cls, dir_paths: tuple[Path, ...]) -> tuple[Path, ...]:
        return tuple(
            (
                Path(f"!{Path(str_path[1:]).expanduser().absolute().resolve()}")
                # maintains the negation prefix if it exists
                if (str_path := str(path)).startswith("!")
                # otherwise, resolve the path normally
                else path.expanduser().absolute().resolve()
            )
            for path in dir_paths
        )

    @property
    def tag_to_level(self) -> dict[str, LevelBump]:
        """A mapping of commit tags to the level bump they should result in."""
        return self._tag_to_level

    @property
    def allowed_tags(self) -> tuple[str, ...]:
        """
        All commit-type prefixes that are allowed.

        These are used to identify a valid commit message. If a commit message does not start with
        one of these prefixes, it will not be considered a valid commit message.

        :return: A tuple of all allowed commit-type prefixes (ordered from most to least significant)
        """
        return tuple(list(self.tag_to_level.keys())[::-1])

    def __post_init__(self) -> None:
        self._tag_to_level: dict[str, LevelBump] = {
            str(tag): level
            for tag, level in [
                # we have to do a type ignore as zip_longest provides a type that is not specific enough
                # for our expected output. Due to the empty second array, we know the first is always longest
                # and that means no values in the first entry of the tuples will ever be a LevelBump. We
                # apply a str() to make mypy happy although it will never happen.
                *zip_longest(
                    self.other_allowed_tags, (), fillvalue=self.default_bump_level
                ),
                *zip_longest(self.patch_tags, (), fillvalue=LevelBump.PATCH),
                *zip_longest(self.minor_tags, (), fillvalue=LevelBump.MINOR),
            ]
            if "|" not in str(tag)
        }


class ConventionalCommitMonorepoParser(
    CommitParser[ParseResult, ConventionalMonorepoParserOptions]
):
    # TODO: Remove for v10 compatibility, get_default_options() will be called instead
    parser_options = ConventionalMonorepoParserOptions

    def __init__(
        self, options: ConventionalMonorepoParserOptions | None = None
    ) -> None:
        super().__init__(options)
        self.file_selection_filters = []
        self.file_ignore_filters = []

        for str_path in map(str, self.options.path_filters):
            str_filter = str_path[1:] if str_path.startswith("!") else str_path
            filter_list = (
                self.file_ignore_filters
                if str_path.startswith("!")
                else self.file_selection_filters
            )

            # Since fnmatch is not too flexible, we will expand the path filters to include the name and any subdirectories
            # as this is how gitignore is interpreted. Possible scenarios:
            # filter: "src" -> [ "src", "src/**"]
            # filter: "src/" -> ["src/**"]
            # filter: "src/*" -> "src/*"
            # filter: "src/**" -> "src/**"
            # This expansion will occur regardless of the negation prefix
            filter_list.extend(
                filter(
                    None,
                    [
                        # Its more likely to be a file within a directory than a specific file, for speed do the directory first
                        (
                            # Set the filter to the directory and all subdirectories if it is not already globbing
                            None
                            if str_path.endswith("*")
                            else f"{str_filter.rstrip(os.sep)}{os.sep}**"
                        ),
                        # Set the filter to the exact file unless its a directory/
                        None if str_path.endswith(os.sep) else str_filter,
                    ],
                )
            )

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

        try:
            commit_scope_pattern = regexp(
                r"\(" + self.options.scope_prefix + r"(?P<scope>[^\n]+)\)",
            )
        except re.error as err:
            raise InvalidParserOptions(
                str.join(
                    "\n",
                    [
                        f"Invalid options for {self.__class__.__name__}",
                        "Unable to create regular expression from configured scope_prefix.",
                        "Please check the configured scope_prefix and remove or escape any regular expression characters.",
                    ],
                )
            ) from err

        # This regular expression includes scope prefix into the pattern and forces a scope to be present
        # PSR will match the full scope but we don't include it in the scope match,
        # which implicitly strips it from being included in the returned scope.
        self.strict_scope_pattern = regexp(
            str.join(
                "",
                [
                    r"^" + commit_type_pattern.pattern,
                    commit_scope_pattern.pattern,
                    r"(?P<break>!)?:\s+",
                    r"(?P<subject>[^\n]+)",
                    r"(?:\n\n(?P<text>.+))?",  # commit body
                ],
            ),
            flags=re.DOTALL,
        )

        self.optional_scope_pattern = regexp(
            str.join(
                "",
                [
                    r"^" + commit_type_pattern.pattern,
                    r"(?:\((?P<scope>[^\n]+)\))?",
                    r"(?P<break>!)?:\s+",
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

    @staticmethod
    def get_default_options() -> ConventionalMonorepoParserOptions:
        return ConventionalMonorepoParserOptions()

    def parse_message(
        self, message: str, strict_scope: bool = False
    ) -> ParsedMessageResult | None:
        if not (parsed := self.strict_scope_pattern.match(message)) and strict_scope:
            return None

        if not parsed and not (parsed := self.optional_scope_pattern.match(message)):
            return None

        parsed_break = parsed.group("break")
        parsed_scope = parsed.group("scope")
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

        linked_merge_request = ""
        if mr_match := self.mr_selector.search(parsed_subject):
            linked_merge_request = mr_match.group("mr_number")
            parsed_subject = self.mr_selector.sub("", parsed_subject).strip()

        body_components: dict[str, list[str]] = reduce(
            self._commit_body_components_separator,
            [
                # Insert the subject before the other paragraphs
                parsed_subject,
                *parse_paragraphs(parsed_text or ""),
            ],
            {
                "breaking_descriptions": [],
                "descriptions": [],
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
            linked_issues=tuple(body_components["linked_issues"]),
            linked_merge_request=linked_merge_request,
        )

    def parse(self, commit: Commit) -> ParseResult:
        """Attempt to parse the commit message with a regular expression into a ParseResult."""
        # Multiple scenarios to consider when parsing a commit message [Truth table]:
        # =======================================================================================================
        # |    ||                         INPUTS                         ||                                     |
        # |  # ||------------------------+----------------+--------------||                Result               |
        # |    || Example Commit Message | Relevant Files | Scope Prefix ||                                     |
        # |----||------------------------+----------------+--------------||-------------------------------------|
        # |  1 || type(prefix-cli): msg  |            yes |    "prefix-" ||                        ParsedCommit |
        # |  2 || type(prefix-cli): msg  |            yes |           "" ||                        ParsedCommit |
        # |  3 || type(prefix-cli): msg  |             no |    "prefix-" ||                        ParsedCommit |
        # |  4 || type(prefix-cli): msg  |             no |           "" ||                ParseError[No files] |
        # |  5 || type(scope-cli): msg   |            yes |    "prefix-" ||                        ParsedCommit |
        # |  6 || type(scope-cli): msg   |            yes |           "" ||                        ParsedCommit |
        # |  7 || type(scope-cli): msg   |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # |  8 || type(scope-cli): msg   |             no |           "" ||                ParseError[No files] |
        # |  9 || type(cli): msg         |            yes |    "prefix-" ||                        ParsedCommit |
        # | 10 || type(cli): msg         |            yes |           "" ||                        ParsedCommit |
        # | 11 || type(cli): msg         |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # | 12 || type(cli): msg         |             no |           "" ||                ParseError[No files] |
        # | 13 || type: msg              |            yes |    "prefix-" ||                        ParsedCommit |
        # | 14 || type: msg              |            yes |           "" ||                        ParsedCommit |
        # | 15 || type: msg              |             no |    "prefix-" ||  ParseError[No files & wrong scope] |
        # | 16 || type: msg              |             no |           "" ||                ParseError[No files] |
        # | 17 || non-conventional msg   |            yes |    "prefix-" ||          ParseError[Invalid Syntax] |
        # | 18 || non-conventional msg   |            yes |           "" ||          ParseError[Invalid Syntax] |
        # | 19 || non-conventional msg   |             no |    "prefix-" ||          ParseError[Invalid Syntax] |
        # | 20 || non-conventional msg   |             no |           "" ||          ParseError[Invalid Syntax] |
        # =======================================================================================================

        # Initial Logic Flow:
        # [1] When there are no relevant files and a scope prefix is defined, we enforce a strict scope
        # [2] When there are no relevant files and no scope prefix is defined, we parse scoped or unscoped commits
        # [3] When there are relevant files, we parse scoped or unscoped commits regardless of any defined prefix
        has_relevant_changed_files = self._has_relevant_changed_files(commit)
        strict_scope = bool(
            not has_relevant_changed_files and self.options.scope_prefix
        )
        pmsg_result = self.parse_message(
            message=str(commit.message),
            strict_scope=strict_scope,
        )

        if pmsg_result and (has_relevant_changed_files or strict_scope):
            logger.debug(
                "commit %s introduces a %s level_bump",
                commit.hexsha[:8],
                pmsg_result.bump,
            )

            return ParsedCommit.from_parsed_message_result(commit, pmsg_result)

        if pmsg_result and not has_relevant_changed_files:
            return _logged_parse_error(
                commit,
                f"Commit {commit.hexsha[:7]} has no changed files matching the path filter(s)",
            )

        if strict_scope and self.parse_message(str(commit.message), strict_scope=False):
            return _logged_parse_error(
                commit,
                str.join(
                    " and ",
                    [
                        f"Commit {commit.hexsha[:7]} has no changed files matching the path filter(s)",
                        f"the scope does not match scope prefix '{self.options.scope_prefix}'",
                    ],
                ),
            )

        return _logged_parse_error(
            commit,
            f"Format Mismatch! Unable to parse commit message: {commit.message!r}",
        )

    def _has_relevant_changed_files(self, commit: Commit) -> bool:
        # Extract git root from commit
        git_root = (
            Path(commit.repo.working_tree_dir or commit.repo.working_dir)
            .absolute()
            .resolve()
        )

        # Check if the changed files of the commit that match the path filters
        for full_path in iter(
            str(git_root / rel_git_path) for rel_git_path in commit.stats.files
        ):
            # Check if the filepath matches any of the file selection filters
            if not any(
                fnmatch(full_path, select_filter)
                for select_filter in self.file_selection_filters
            ):
                continue

            # Pass filter matches, so now evaluate if it is supposed to be ignored
            if not any(
                fnmatch(full_path, ignore_filter)
                for ignore_filter in self.file_ignore_filters
            ):
                # No ignore filter matched, so it must be a relevant file
                return True

        return False

    def _commit_body_components_separator(
        self, accumulator: dict[str, list[str]], text: str
    ) -> dict[str, list[str]]:
        if match := breaking_re.match(text):
            accumulator["breaking_descriptions"].append(match.group(1) or "")
            return accumulator

        if match := self.issue_selector.search(text):
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
            accumulator["linked_issues"] = sort_numerically(
                set(accumulator["linked_issues"]).union(new_issue_refs)
            )
            return accumulator

        # Prevent appending duplicate descriptions
        if text not in accumulator["descriptions"]:
            accumulator["descriptions"].append(text)

        return accumulator
