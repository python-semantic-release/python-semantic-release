from semantic_release.dist import build_dists, should_build, should_remove_dist

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


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {
                "upload_to_pypi": True,
                "upload_to_release": True,
                "build_command": "python setup.py build",
            },
            True,
        ),
        (
            {"upload_to_pypi": True, "upload_to_release": True, "build_command": False},
            False,
        ),
        (
            {"upload_to_pypi": True, "upload_to_release": True, "build_command": None},
            False,
        ),
        (
            {"upload_to_pypi": True, "upload_to_release": True, "build_command": ""},
            False,
        ),
        (
            {
                "upload_to_pypi": True,
                "upload_to_release": True,
                "build_command": "false",
            },
            False,
        ),
        (
            {
                "upload_to_pypi": False,
                "upload_to_release": True,
                "build_command": "python setup.py build",
            },
            True,
        ),
        (
            {
                "upload_to_pypi": True,
                "upload_to_release": False,
                "build_command": "python setup.py build",
            },
            True,
        ),
        (
            {
                "upload_to_pypi": False,
                "upload_to_release": False,
                "build_command": "python setup.py build",
            },
            False,
        ),
    ],
)
def test_should_build(config, expected, mocker):
    mocker.patch("semantic_release.cli.config.get", lambda key: config.get(key))
    assert should_build() == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {
                "upload_to_pypi": True,
                "upload_to_release": True,
                "build_command": "python setup.py build",
                "remove_dist": True,
            },
            True,
        ),
        (
            {
                "upload_to_pypi": True,
                "upload_to_release": True,
                "build_command": "python setup.py build",
                "remove_dist": False,
            },
            False,
        ),
        (
            {
                "upload_to_pypi": False,
                "upload_to_release": False,
                "build_command": False,
                "remove_dist": True,
            },
            False,
        ),
        (
            {
                "upload_to_pypi": False,
                "upload_to_release": False,
                "build_command": "false",
                "remove_dist": True,
            },
            False,
        ),
    ],
)
def test_should_remove_dist(config, expected, mocker):
    mocker.patch("semantic_release.cli.config.get", lambda key: config.get(key))
    assert should_remove_dist() == expected
