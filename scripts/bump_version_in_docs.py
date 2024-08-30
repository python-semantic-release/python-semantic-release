# ruff: noqa: T201, allow print statements in non-prod scripts
from __future__ import annotations

from os import getenv
from pathlib import Path
from re import compile as RegExp  # noqa: N812

PROJ_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJ_DIR / "docs"


def update_github_actions_example(filepath: Path, new_version: str) -> None:
    psr_regex = RegExp(r"(uses:.*python-semantic-release)@v\d+\.\d+\.\d+")
    file_content_lines = filepath.read_text().splitlines()

    for regex in [psr_regex]:
        file_content_lines = list(
            map(
                lambda line, regex=regex: regex.sub(r"\1@v" + new_version, line),
                file_content_lines,
            )
        )

    print(f"Bumping version in {filepath} to", new_version)
    filepath.write_text(str.join("\n", file_content_lines) + "\n")


if __name__ == "__main__":
    new_version = getenv("NEW_VERSION")

    if not new_version:
        print("NEW_VERSION environment variable is not set")
        exit(1)

    update_github_actions_example(
        DOCS_DIR / "automatic-releases" / "github-actions.rst", new_version
    )
