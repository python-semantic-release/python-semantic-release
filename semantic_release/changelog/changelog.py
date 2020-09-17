from typing import Iterable, Optional

from ..settings import config


def get_changelog_sections(changelog: dict, changelog_sections: list) -> Iterable[str]:
    """Generator which yields each changelog section to be included"""

    included_sections = config.get("changelog_sections")
    included_sections = [s.strip() for s in included_sections.split(",")]

    for section in included_sections:
        if section in changelog and changelog[section]:
            yield section


def get_hash_url(owner: str, repo_name: str, hash_: str) -> str:
    if config.get("hvcs") == "gitlab":
        return f"https://gitlab.com/{owner}/{repo_name}/-/commit/{hash_}"
    return f"https://github.com/{owner}/{repo_name}/commit/{hash_}"


def changelog_headers(
    owner: str, repo_name: str, changelog: dict, changelog_sections: list, **kwargs
) -> Optional[str]:
    output = ""

    for section in get_changelog_sections(changelog, changelog_sections):
        # Add a header for this section
        output += "\n### {0}\n".format(section.capitalize())

        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            output += (
                f"* {item[1]} ([{item[0]}]"
                f"({get_hash_url(owner, repo_name, item[0])}))\n"
            )

    return output


def changelog_table(
    owner: str, repo_name: str, changelog: dict, changelog_sections: list, **kwargs
) -> str:
    output = "| Type | Change |\n| --- | --- |\n"

    for section in get_changelog_sections(changelog, changelog_sections):
        items = "<br>".join(
            [
                f"{item[1]} ([{item[0]}]({get_hash_url(owner, repo_name, item[0])}))"
                for item in changelog[section]
            ]
        )
        output += f"| {section.title()} | {items} |\n"

    return output
