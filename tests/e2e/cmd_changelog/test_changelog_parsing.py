from __future__ import annotations

import os
import shutil
from pathlib import Path
from re import MULTILINE, compile as regexp
from typing import TYPE_CHECKING

import pytest
from pytest_lazy_fixtures.lazy_fixture import lf as lazy_fixture

from semantic_release.changelog.context import ChangelogMode
from semantic_release.cli.const import JINJA2_EXTENSION

from tests.const import CHANGELOG_SUBCMD, MAIN_PROG_NAME
from tests.fixtures.example_project import (
    default_changelog_md_template,
    default_changelog_rst_template,
    default_md_changelog_insertion_flag,
    default_rst_changelog_insertion_flag,
    example_changelog_md,
    example_changelog_rst,
)
from tests.fixtures.repos.git_flow import (
    repo_w_git_flow_conventional_commits,
    repo_w_git_flow_scipy_commits,
)
from tests.util import assert_successful_exit_code

if TYPE_CHECKING:
    from tests.conftest import RunCliFn
    from tests.fixtures.example_project import UpdatePyprojectTomlFn
    from tests.fixtures.git_repo import BuiltRepoResult


@pytest.mark.parametrize(
    "changelog_file, insertion_flag, default_changelog_template, changes_tpl_file",
    [
        (
            # ChangelogOutputFormat.MARKDOWN
            lazy_fixture(example_changelog_md.__name__),
            lazy_fixture(default_md_changelog_insertion_flag.__name__),
            lazy_fixture(default_changelog_md_template.__name__),
            Path(".components", "changes.md.j2"),
        ),
        (
            # ChangelogOutputFormat.RESTRUCTURED_TEXT
            lazy_fixture(example_changelog_rst.__name__),
            lazy_fixture(default_rst_changelog_insertion_flag.__name__),
            lazy_fixture(default_changelog_rst_template.__name__),
            Path(".components", "changes.rst.j2"),
        ),
    ],
)
@pytest.mark.parametrize(
    "repo_result",
    [
        pytest.param(
            lazy_fixture(repo_fixture_name),
            marks=pytest.mark.comprehensive,
        )
        for repo_fixture_name in [
            repo_w_git_flow_conventional_commits.__name__,
            repo_w_git_flow_scipy_commits.__name__,
        ]
    ],
)
def test_changelog_parsing_ignore_merge_commits(
    run_cli: RunCliFn,
    repo_result: BuiltRepoResult,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    example_project_template_dir: Path,
    changelog_file: Path,
    insertion_flag: str,
    default_changelog_template: Path,
    changes_tpl_file: Path,
):
    repo = repo_result["repo"]
    expected_changelog_content = changelog_file.read_text()

    update_pyproject_toml(
        "tool.semantic_release.commit_parser_options.ignore_merge_commits", True
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.mode", ChangelogMode.UPDATE.value
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.insertion_flag",
        insertion_flag,
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.template_dir",
        str(example_project_template_dir.relative_to(repo.working_dir)),
    )
    update_pyproject_toml(
        "tool.semantic_release.changelog.exclude_commit_patterns",
        [
            r"""Initial Commit.*""",
        ],
    )

    # Force custom changelog to be a copy of the default changelog
    shutil.copytree(
        src=default_changelog_template.parent,
        dst=example_project_template_dir,
        dirs_exist_ok=True,
    )

    # Remove the "unknown" filter from the changelog template to enable Merge commits
    patch = regexp(
        r'^(#}{% *for type_, commits in commit_objects) if type_ != "unknown"',
        MULTILINE,
    )
    changes_file = example_project_template_dir.joinpath(changes_tpl_file)
    changes_file.write_text(patch.sub(r"\1", changes_file.read_text()))

    # Make sure the prev_changelog_file is the same as the current changelog
    changelog_tpl_file = example_project_template_dir.joinpath(
        changelog_file.name
    ).with_suffix(str.join("", [changelog_file.suffix, JINJA2_EXTENSION]))
    changelog_tpl_file.write_text(
        regexp(r"= ctx.prev_changelog_file").sub(
            rf'= "{changelog_file.name}"', changelog_tpl_file.read_text()
        )
    )

    # Remove the changelog to force re-generation with new configurations
    os.remove(str(changelog_file.resolve()))

    # Act
    cli_cmd = [MAIN_PROG_NAME, CHANGELOG_SUBCMD]
    result = run_cli(cli_cmd[1:])

    # Evaluate
    assert_successful_exit_code(result, cli_cmd)
    assert expected_changelog_content == changelog_file.read_text()
