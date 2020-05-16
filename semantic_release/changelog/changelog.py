from ..settings import config


def changelog_sections(changelog):
    """Generator which yields each changelog section to be included"""

    included_sections = config.get("semantic_release", "changelog_sections")
    included_sections = [s.strip() for s in included_sections.split(",")]

    for section in included_sections:
        if section in changelog and changelog[section]:
            yield section


def changelog_headers(changelog, **kwargs):
    output = ""

    for section in changelog_sections(changelog):
        # Add a header for this section
        output += "\n### {0}\n".format(section.capitalize())

        # Add each commit from the section in an unordered list
        for item in changelog[section]:
            output += "* {0} ({1})\n".format(item[1], item[0])

    return output

