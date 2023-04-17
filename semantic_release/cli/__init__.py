from semantic_release.cli.commands.changelog import changelog as changelog
from semantic_release.cli.commands.generate_config import generate_config
from semantic_release.cli.commands.main import main as main
from semantic_release.cli.commands.publish import publish
from semantic_release.cli.commands.version import version as version

main.add_command(changelog)
main.add_command(generate_config)
main.add_command(version)
main.add_command(publish)
