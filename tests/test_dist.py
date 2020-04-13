from semantic_release.dist import build_dists

from . import pytest


@pytest.mark.parametrize(
    "commands",
    ["sdist bdist_wheel", "sdist", "bdist_wheel", "sdist bdist_wheel custom_cmd"],
)
def test_build_command(mocker, commands):
    mocker.patch("semantic_release.dist.config.get", lambda *a: commands)
    mock_run = mocker.patch("semantic_release.dist.run")
    build_dists()
    mock_run.assert_called_once_with(commands)
