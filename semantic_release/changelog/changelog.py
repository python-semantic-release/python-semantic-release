from typing import Iterable, Optional

from ..settings import config


def get_changelog_sections(changelog: dict, changelog_sections: list) -> Iterable[str]:
    """Generator which yields each changelog section to be included"""

    included_sections = config.get("changelog_sections")
    included_sections = [s.strip() for s in included_sections.split(",")]

    for section in included_sections:
        if section in changelog and changelog[section]:
            yield section


def changelog_headers(
    changelog: dict, changelog_sections: list, **kwargs
) -> Optional[str]:
    output = ""

    for section in get_changelog_sections(changelog, changelog_sections):
        # Add a header for this section
        output += "\n### {0}\n".format(section.capitalize())

        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            output += "* {0} ({1})\n".format(item[1], item[0])

    return output


def changelog_table(changelog: dict, changelog_sections: list, **kwargs) -> str:
    output = "| Type | Change |\n| --- | --- |\n"

    for section in get_changelog_sections(changelog, changelog_sections):
        items = "<br>".join([f"{item[1]} ({item[0]})" for item in changelog[section]])
        output += f"| {section.title()} | {items} |\n"

    return output
