import logging

import pytest

from semantic_release import __version__
from semantic_release.cli import main


def test_main_prints_version_and_exits(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"semantic-release, version {__version__}\n"


@pytest.mark.parametrize("args", [[], ["--help"]])
def test_main_prints_help_text(runner, args):
    result = runner.invoke(main, args)
    assert result.exit_code == 0
