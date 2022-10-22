# import sys

from semantic_release.cli.commands.changelog import changelog
from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.commands.main import main
from semantic_release.cli.commands.publish import publish
from semantic_release.cli.commands.version import version

main.add_command(changelog)
main.add_command(generate_config)
main.add_command(version)
main.add_command(publish)

"""
def entry() -> None:
    # Move flags to after the command
    # args = sorted(sys.argv[1:], key=lambda x: 1 if x.startswith("--") else -1)
    main(args=sys.argv[1:])
"""
