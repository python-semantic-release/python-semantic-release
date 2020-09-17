import logging

from ..helpers import LoggedFunction
from ..settings import config, current_changelog_components

from .changelog import changelog_headers, changelog_table  # noqa isort:skip
from .compare import compare_url  # noqa isort:skip

logger = logging.getLogger(__name__)


@LoggedFunction(logger)
def markdown_changelog(
    owner: str,
    repo_name: str,
    version: str,
    changelog: dict,
    header: bool = False,
    previous_version: str = None,
) -> str:
    """
    Generate a markdown version of the changelog.

    :param owner: The repo owner.
    :param repo_name: The repo name.
    :param version: A string with the version number.
    :param previous_version: A string with the last version number, to
        use for the comparison URL. If omitted, the URL will not be included.
    :param changelog: A parsed changelog dict from generate_changelog.
    :param header: A boolean that decides whether a version number header should be included.
    :return: The markdown formatted changelog.
    """
    output = f"## v{version}\n" if header else ""

    # Add the output of each component separated by a blank line
    output += "\n\n".join(
        (
            component_output.strip()
            for component_output in (
                component(
                    owner=owner,
                    repo_name=repo_name,
                    version=version,
                    previous_version=previous_version,
                    changelog=changelog,
                    changelog_sections=config.get("changelog_sections").split(","),
                )
                for component in current_changelog_components()
            )
            if component_output is not None
        )
    )

    return output
