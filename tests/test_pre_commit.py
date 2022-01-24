from semantic_release.pre_commit import run_pre_commit, should_run_pre_commit

import pytest


@pytest.mark.parametrize(
    "commands",
    ["make do-stuff", "echo hello > somefile.txt"],
)
def test_pre_commit_command(mocker, commands):
    mocker.patch("semantic_release.pre_commit.config.get", lambda *a: commands)
    mock_run = mocker.patch("semantic_release.pre_commit.run")
    run_pre_commit()
    mock_run.assert_called_once_with(commands)


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {
                "pre_commit_command": "make generate_some_file",
            },
            True,
        ),
        (
            {
                "pre_commit_command": "cmd",
            },
            True,
        ),
        (
            {
                "pre_commit_command": "",
            },
            False,
        ),
        (
            {},
            False,
        ),
    ],
)
def test_should_run_pre_commit_command(config, expected, mocker):
    mocker.patch("semantic_release.cli.config.get", lambda key: config.get(key))
    assert should_run_pre_commit() == expected
