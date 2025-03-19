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

# typing_extensions is for Python 3.8, 3.9, 3.10 compatibility
from typing_extensions import Annotated

from semantic_release.commit_parser._base import CommitParser, ParserOptions
from semantic_release.commit_parser.angular import LONG_TYPE_NAMES
from semantic_release.commit_parser.conventional.options_monorepo import ConventionalMonorepoParserOptions
from semantic_release.commit_parser.conventional.parser import ConventionalCommitParser
from semantic_release.commit_parser.token import (
    ParsedCommit,
    ParsedMessageResult,
    ParseError,
    ParseResult,
)
from semantic_release.commit_parser.util import (
    breaking_re,
    force_str,
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


class ConventionalCommitMonorepoParser(ConventionalCommitParser):

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
        parsed_scope = parsed.group("scope") or ""
        parsed_subject = parsed.group("subject")
        parsed_text = parsed.group("text")
        parsed_type = parsed.group("type")

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

    def parse_commit(self, commit: Commit) -> ParseResult:
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
            message=force_str(commit.message),
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
