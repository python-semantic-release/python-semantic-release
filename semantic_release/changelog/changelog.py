import re
from typing import Iterable, Optional

from ..hvcs import Github, Gitlab
from ..settings import config


def add_pr_link(owner: str, repo_name: str, message: str) -> str:
    """
    GitHub release notes automagically link to the PR, but changelog markdown
    doesn't. Replace (#123) at the end of a message with a markdown link.
    """

    pr_pattern = re.compile(r"\s+\(#(\d{1,8})\)$")
    match = re.search(pr_pattern, message)

    if match:
        pr_number = match.group(1)
        url = (
            f"https://{Gitlab.domain()}/{owner}/{repo_name}/-/issues/{pr_number}"
            if config.get("hvcs") == "gitlab"
            else f"https://{Github.domain()}/{owner}/{repo_name}/issues/{pr_number}"
        )

        return re.sub(pr_pattern, f" ([#{pr_number}]({url}))", message)

    return message


def get_changelog_sections(changelog: dict, changelog_sections: list) -> Iterable[str]:
    """Generator which yields each changelog section to be included"""

    included_sections = config.get("changelog_sections")
    included_sections = [s.strip() for s in included_sections.split(",")]

    for section in included_sections:
        if section in changelog and changelog[section]:
            yield section


def get_hash_link(owner: str, repo_name: str, hash_: str) -> str:
    """Generate the link for commit hash"""
    url = (
        f"https://{Gitlab.domain()}/{owner}/{repo_name}/-/commit/{hash_}"
        if config.get("hvcs") == "gitlab"
        else f"https://{Github.domain()}/{owner}/{repo_name}/commit/{hash_}"
    )
    short_hash = hash_[:7]
    return f"[`{short_hash}`]({url})"


def changelog_headers(
    owner: str, repo_name: str, changelog: dict, changelog_sections: list, **kwargs
) -> Optional[str]:
    output = ""

    for section in get_changelog_sections(changelog, changelog_sections):
        # Add a header for this section
        output += f"\n### {section.capitalize()}\n"

        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            message = add_pr_link(owner, repo_name, item[1])
            output += f"* {message} ({get_hash_link(owner, repo_name, item[0])})\n"

    return output


def changelog_table(
    owner: str, repo_name: str, changelog: dict, changelog_sections: list, **kwargs
) -> str:
    output = "| Type | Change |\n| --- | --- |\n"

    for section in get_changelog_sections(changelog, changelog_sections):
        items = "<br>".join(
            [
                f"{add_pr_link(owner, repo_name, item[1])} "
                f"({get_hash_link(owner, repo_name, item[0])})"
                for item in changelog[section]
            ]
        )
        output += f"| {section.title()} | {items} |\n"

    return output
