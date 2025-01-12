# ruff: noqa: T201, allow print statements in non-prod scripts
from __future__ import annotations

from os import getenv
from pathlib import Path
from re import compile as regexp

PROJ_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJ_DIR / "docs"


def update_github_actions_example(filepath: Path, release_tag: str) -> None:
    psr_regex = regexp(r"(uses: python-semantic-release/python-semantic-release)@\S+$")
    psr_publish_action_regex = regexp(
        r"(uses: python-semantic-release/publish-action)@\S+$"
    )
    file_content_lines: list[str] = filepath.read_text().splitlines()

    for regex in [psr_regex, psr_publish_action_regex]:
        file_content_lines = list(
            map(
                lambda line, regex=regex: regex.sub(r"\1@" + release_tag, line),  # type: ignore[misc]
                file_content_lines,
            )
        )

    print(f"Bumping version in {filepath} to", release_tag)
    filepath.write_text(str.join("\n", file_content_lines) + "\n")


if __name__ == "__main__":
    new_release_tag = getenv("NEW_RELEASE_TAG")

    if not new_release_tag:
        print("NEW_RELEASE_TAG environment variable is not set")
        exit(1)

    update_github_actions_example(
        DOCS_DIR / "automatic-releases" / "github-actions.rst", new_release_tag
    )
