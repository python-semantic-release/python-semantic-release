import pytest

from semantic_release.cli import changelog, generate_config, main, publish, version


@pytest.mark.parametrize("help_option", ("-h", "--help"))
@pytest.mark.parametrize(
    "command",
    (main, changelog, generate_config, publish, version),
    ids=lambda cmd: cmd.name,
)
def test_help(help_option, command, cli_runner):
    result = cli_runner.invoke(command, [help_option])

    assert result.exit_code == 0
    # commands have help text
    assert result.output

    if command is not main:
        # commands have their own unique help text
        assert result.output != cli_runner.invoke(main, [help_option]).output
