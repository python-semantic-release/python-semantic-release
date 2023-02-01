from click.testing import CliRunner

from semantic_release.cli import changelog, main, print_version, publish, version
from semantic_release.errors import GitError, ImproperConfigurationError
from semantic_release.repository import ArtifactRepo

from . import mock, pytest, reset_config, wrapped_config_get
from .mocks import mock_version_file

assert reset_config


@pytest.fixture
def runner():
    return CliRunner()


def test_main_should_call_correct_function(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_version_by_commit_should_call_correct_functions(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            commit_version_number=True,
        ),
    )
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new_version = mocker.patch("semantic_release.cli.commit_new_version")
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    mock_set_new_version.assert_called_once_with("2.0.0")
    mock_commit_new_version.assert_called_once_with("2.0.0")
    mock_tag_new_version.assert_called_once_with("2.0.0")


def test_version_by_tag_with_commit_version_number_should_call_correct_functions(
    mocker,
):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            version_source="tag",
            commit_version_number=True,
        ),
    )

    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new_version = mocker.patch("semantic_release.cli.commit_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    mock_set_new_version.assert_called_once_with("2.0.0")
    mock_commit_new_version.assert_called_once_with("2.0.0")
    mock_tag_new_version.assert_called_once_with("2.0.0")


def test_version_by_tag_only_with_commit_version_number_should_call_correct_functions(
    mocker,
):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            version_source="tag_only",
            commit_version_number=True,
        ),
    )

    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new_version = mocker.patch("semantic_release.cli.commit_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once_with()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    assert not mock_set_new_version.called
    assert not mock_commit_new_version.called
    mock_tag_new_version.assert_called_once_with("2.0.0")


def test_version_by_tag_should_call_correct_functions(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(version_source="tag"),
    )
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    mock_set_new_version.assert_called_once_with("2.0.0")
    mock_tag_new_version.assert_called_once_with("2.0.0")


def test_version_by_tag_only_should_call_correct_functions(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(version_source="tag_only"),
    )
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once_with()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    assert not mock_set_new_version.called
    mock_tag_new_version.assert_called_once_with("2.0.0")


def test_version_by_commit_without_tag_should_call_correct_functions(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(version_source="commit", tag_commit=False),
    )
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new_version = mocker.patch("semantic_release.cli.commit_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="2.0.0"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", "major", False, True)
    mock_set_new_version.assert_called_once_with("2.0.0")
    mock_commit_new_version.assert_called_once_with("2.0.0")
    assert not mock_tag_new_version.called


def test_force_major(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version", "--major"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level="major",
        prerelease=False,
        prerelease_patch=True,
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]["force_level"] == "major"
    assert result.exit_code == 0


def test_force_minor(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version", "--minor"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level="minor",
        prerelease=False,
        prerelease_patch=True,
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]["force_level"] == "minor"
    assert result.exit_code == 0


def test_force_patch(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version", "--patch"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level="patch",
        prerelease=False,
        prerelease_patch=True,
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]["force_level"] == "patch"
    assert result.exit_code == 0


def test_retry(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version", "--retry"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        retry=True,
        define=(),
    )
    assert result.exit_code == 0


def test_prerelease_patch(mocker, runner):
    mock_version = mocker.patch("semantic_release.cli.version")
    result = runner.invoke(main, ["version", "--no-prerelease-patch"])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_noop_mode(mocker):
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_set_new = mocker.patch("semantic_release.cli.commit_new_version")
    mock_commit_new = mocker.patch("semantic_release.cli.set_new_version")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")

    version(noop=True)

    assert not mock_set_new.called
    assert not mock_commit_new.called
    assert not mock_tag_new_version.called


def test_cli_print_version(mocker, runner):
    mock_print_version = mocker.patch("semantic_release.cli.print_version")
    result = runner.invoke(main, ["print-version"])
    mock_print_version.assert_called_once_with(
        current=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        noop=False,
        post=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_cli_print_version_force_major(mocker, runner):
    mock_print_version = mocker.patch("semantic_release.cli.print_version")
    result = runner.invoke(main, ["print-version", "--major"])
    mock_print_version.assert_called_once_with(
        current=False,
        force_level="major",
        prerelease=False,
        prerelease_patch=True,
        noop=False,
        post=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_cli_print_version_prerelease(mocker, runner):
    mock_print_version = mocker.patch("semantic_release.cli.print_version")
    result = runner.invoke(main, ["print-version", "--prerelease"])
    mock_print_version.assert_called_once_with(
        current=False,
        force_level=None,
        prerelease=True,
        prerelease_patch=True,
        noop=False,
        post=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_cli_print_version_current(mocker, runner):
    mock_print_version = mocker.patch("semantic_release.cli.print_version")
    result = runner.invoke(main, ["print-version", "--current"])
    mock_print_version.assert_called_once_with(
        current=True,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        noop=False,
        post=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_cli_print_version_next(mocker, runner):
    mock_print_version = mocker.patch("semantic_release.cli.print_version")
    result = runner.invoke(main, ["print-version", "--next"])
    mock_print_version.assert_called_once_with(
        current=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        noop=False,
        post=False,
        retry=False,
        define=(),
    )
    assert result.exit_code == 0


def test_print_version_no_change(mocker, runner, capsys):
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value=None
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    print_version()
    outerr = capsys.readouterr()
    assert outerr.out == ""
    assert outerr.err == "No release will be made.\n"

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", None, False, True)


def test_print_version_change(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="minor"
    )

    print_version()
    outerr = capsys.readouterr()
    assert outerr.out == "1.3.0"
    assert outerr.err == ""

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)


def test_print_version_change_prerelease(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="minor"
    )

    print_version(prerelease=True)
    outerr = capsys.readouterr()
    assert outerr.out == "1.3.0-beta.1"
    assert outerr.err == ""

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)


def test_print_version_change_prerelease_no_patch(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value=None
    )

    print_version(prerelease=True, prerelease_patch=False)
    outerr = capsys.readouterr()
    assert outerr.out == ""
    assert outerr.err == "No release will be made.\n"

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)


def test_print_version_change_prerelease_bump(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="minor"
    )

    print_version(prerelease=True)
    outerr = capsys.readouterr()
    assert outerr.out == "1.3.0-beta.1"
    assert outerr.err == ""

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)


def test_print_version_force_major(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )

    print_version(force_level="major")
    outerr = capsys.readouterr()
    assert outerr.out == "2.0.0"
    assert outerr.err == ""

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", "major")


def test_print_version_force_major_prerelease(mocker, runner, capsys):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="major"
    )

    print_version(force_level="major", prerelease=True)
    outerr = capsys.readouterr()
    assert outerr.out == "2.0.0-beta.1"
    assert outerr.err == ""

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", "major")


def test_version_no_change(mocker, runner):
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new_version = mocker.patch("semantic_release.cli.commit_new_version")
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_new_version = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value=None
    )
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )

    version()

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", None)
    mock_new_version.assert_called_once_with("1.2.3", "1.2.3", None, False, True)
    assert not mock_set_new_version.called
    assert not mock_commit_new_version.called
    assert not mock_tag_new_version.called


def test_version_check_build_status_fails(mocker):
    mock_check_build_status = mocker.patch(
        "semantic_release.cli.check_build_status", return_value=False
    )
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mock_commit_new = mocker.patch("semantic_release.cli.commit_new_version")
    mock_set_new = mocker.patch("semantic_release.cli.set_new_version")
    mocker.patch("semantic_release.cli.config.get", lambda *x: True)
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")

    version()

    assert mock_check_build_status.called
    assert not mock_set_new.called
    assert not mock_commit_new.called
    assert not mock_tag_new_version.called


def test_version_by_commit_check_build_status_succeeds(mocker):
    mocker.patch("semantic_release.cli.config.get", lambda *x, **y: True)
    mock_check_build_status = mocker.patch(
        "semantic_release.cli.check_build_status", return_value=True
    )
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")
    mock_commit_new = mocker.patch("semantic_release.cli.commit_new_version")
    mock_set_new = mocker.patch("semantic_release.cli.set_new_version")

    version()

    assert mock_check_build_status.called
    assert mock_set_new.called
    assert mock_commit_new.called
    assert mock_tag_new_version.called


def test_version_by_tag_check_build_status_succeeds(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            version_source="tag",
            commit_version_number=False,
            check_build_status=True,
        ),
    )
    mock_check_build_status = mocker.patch(
        "semantic_release.cli.check_build_status", return_value=True
    )
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")

    version()

    assert mock_check_build_status.called
    assert mock_set_new_version.called
    assert mock_tag_new_version.called


def test_version_by_tag_only_check_build_status_succeeds(mocker):
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            version_source="tag_only",
            commit_version_number=False,
            check_build_status=True,
        ),
    )
    mock_check_build_status = mocker.patch(
        "semantic_release.cli.check_build_status", return_value=True
    )
    mock_set_new_version = mocker.patch("semantic_release.cli.set_new_version")
    mock_tag_new_version = mocker.patch("semantic_release.cli.tag_new_version")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")

    version()

    assert mock_check_build_status.called
    assert not mock_set_new_version.called
    assert mock_tag_new_version.called


def test_version_check_build_status_not_called_if_disabled(mocker):
    mock_check_build_status = mocker.patch("semantic_release.cli.check_build_status")
    mocker.patch("semantic_release.cli.config.get", lambda *x, **y: False)
    mocker.patch("semantic_release.cli.tag_new_version")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "major")
    mocker.patch("semantic_release.cli.commit_new_version")
    mocker.patch("semantic_release.cli.set_new_version")

    version()

    assert not mock_check_build_status.called


def test_version_retry_and_giterror(mocker):
    mocker.patch(
        "semantic_release.cli.get_current_version", mock.Mock(side_effect=GitError())
    )

    result = version(retry=True)

    assert not result


def test_version_retry(mocker):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate_bump = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="patch"
    )
    mock_get_new = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="new"
    )
    mocker.patch("semantic_release.cli.config.get", lambda *x: False)

    result = version(noop=False, retry=True, force_level=False)

    assert result
    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate_bump.assert_called_once_with("1.2.3", False)
    mock_get_new.assert_called_once_with("1.2.3", "1.2.3", "patch", False, True)


def test_publish_should_not_run_pre_commit_by_default(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.ci_checks.check")
    mocker.patch.object(ArtifactRepo, "upload")
    mocker.patch("semantic_release.cli.upload_to_release")
    mocker.patch("semantic_release.cli.post_changelog", lambda *x: True)
    mocker.patch("semantic_release.cli.push_new_version", return_value=True)
    mocker.patch("semantic_release.cli.should_bump_version", return_value=True)
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)
    run_pre_commit = mocker.patch("semantic_release.cli.run_pre_commit")
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            remove_dist=False,
            upload_to_pypi=False,
            upload_to_release=False,
        ),
    )
    mocker.patch("semantic_release.cli.update_changelog_file", lambda *x, **y: None)

    publish()

    assert not run_pre_commit.called


def test_publish_should_not_run_pre_commit_with_empty_command(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.ci_checks.check")
    mocker.patch.object(ArtifactRepo, "upload")
    mocker.patch("semantic_release.cli.upload_to_release")
    mocker.patch("semantic_release.cli.post_changelog", lambda *x: True)
    mocker.patch("semantic_release.cli.push_new_version", return_value=True)
    mocker.patch("semantic_release.cli.should_bump_version", return_value=True)
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)
    run_pre_commit = mocker.patch("semantic_release.cli.run_pre_commit")
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            remove_dist=False,
            upload_to_pypi=False,
            upload_to_release=False,
            pre_commit_command="",
        ),
    )
    mocker.patch("semantic_release.cli.update_changelog_file", lambda *x, **y: None)

    publish()

    assert not run_pre_commit.called


def test_publish_should_run_pre_commit_if_provided(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.ci_checks.check")
    mocker.patch.object(ArtifactRepo, "upload")
    mocker.patch("semantic_release.cli.upload_to_release")
    mocker.patch("semantic_release.cli.post_changelog", lambda *x: True)
    mocker.patch("semantic_release.cli.push_new_version", return_value=True)
    mocker.patch("semantic_release.cli.should_bump_version", return_value=True)
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)
    run_pre_commit = mocker.patch("semantic_release.cli.run_pre_commit")
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            remove_dist=False,
            upload_to_pypi=False,
            upload_to_release=False,
            pre_commit_command='echo "Hello, world."',
        ),
    )
    mocker.patch("semantic_release.cli.update_changelog_file", lambda *x, **y: None)

    publish()

    assert run_pre_commit.called


def test_publish_should_not_upload_to_pypi_if_option_is_false(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.ci_checks.check")
    mock_repository = mocker.patch.object(ArtifactRepo, "upload")
    mock_upload_release = mocker.patch("semantic_release.cli.upload_to_release")
    mocker.patch("semantic_release.cli.post_changelog", lambda *x: True)
    mocker.patch("semantic_release.cli.push_new_version", return_value=True)
    mocker.patch("semantic_release.cli.should_bump_version", return_value=False)
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            remove_dist=False,
            upload_to_pypi=False,
            upload_to_release=False,
        ),
    )
    mocker.patch("semantic_release.cli.update_changelog_file", lambda *x, **y: None)

    publish()

    assert not mock_repository.called
    assert not mock_upload_release.called


def test_publish_should_not_upload_to_repository_if_option_is_false(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.ci_checks.check")
    mock_repository = mocker.patch.object(ArtifactRepo, "upload")
    mock_upload_release = mocker.patch("semantic_release.cli.upload_to_release")
    mocker.patch("semantic_release.cli.post_changelog", lambda *x: True)
    mocker.patch("semantic_release.cli.push_new_version", return_value=True)
    mocker.patch("semantic_release.cli.should_bump_version", return_value=False)
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            remove_dist=False,
            upload_to_repository=False,
            upload_to_release=False,
        ),
    )
    mocker.patch("semantic_release.cli.update_changelog_file", lambda *x, **y: None)

    publish()

    assert not mock_repository.called
    assert not mock_upload_release.called


def test_publish_should_do_nothing_when_not_should_bump_version(mocker):
    mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "feature")
    mocker.patch("semantic_release.cli.generate_changelog")
    mock_log = mocker.patch("semantic_release.cli.post_changelog")
    mock_repository = mocker.patch.object(ArtifactRepo, "upload")
    mock_upload_release = mocker.patch("semantic_release.cli.upload_to_release")
    mock_push = mocker.patch("semantic_release.cli.push_new_version")
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mock_should_bump_version = mocker.patch(
        "semantic_release.cli.should_bump_version", return_value=False
    )

    publish()

    assert mock_should_bump_version.called
    assert not mock_push.called
    assert not mock_repository.called
    assert not mock_upload_release.called
    assert not mock_log.called
    assert mock_ci_check.called


def test_publish_should_call_functions(mocker):
    mock_push = mocker.patch("semantic_release.cli.push_new_version")
    mock_checkout = mocker.patch("semantic_release.cli.checkout")
    mock_should_bump_version = mocker.patch(
        "semantic_release.cli.should_bump_version", return_value=True
    )
    mock_log = mocker.patch("semantic_release.cli.post_changelog")
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mocker.patch.dict(
        "os.environ",
        {
            "REPOSITORY_USERNAME": "repo-username",
            "REPOSITORY_PASSWORD": "repo-password",
        },
    )
    mock_repository = mocker.patch.object(ArtifactRepo, "upload")
    mock_release = mocker.patch("semantic_release.cli.upload_to_release")
    mock_build_dists = mocker.patch("semantic_release.cli.build_dists")
    mock_remove_dists = mocker.patch("semantic_release.cli.remove_dists")
    mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("relekang", "python-semantic-release"),
    )
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "feature")
    mocker.patch("semantic_release.cli.generate_changelog")
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)

    publish()

    assert mock_ci_check.called
    assert mock_push.called
    assert mock_remove_dists.called
    assert mock_build_dists.called
    assert mock_repository.called
    assert mock_release.called
    assert mock_should_bump_version.called
    mock_log.assert_called_once_with(
        "relekang", "python-semantic-release", "2.0.0", "CHANGES"
    )
    mock_checkout.assert_called_once_with("master")


def test_publish_should_skip_build_when_command_is_empty(mocker):
    mock_push = mocker.patch("semantic_release.cli.push_new_version")
    mock_checkout = mocker.patch("semantic_release.cli.checkout")
    mock_should_bump_version = mocker.patch(
        "semantic_release.cli.should_bump_version", return_value=True
    )
    mock_log = mocker.patch("semantic_release.cli.post_changelog")
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mocker.patch.dict(
        "os.environ",
        {
            "REPOSITORY_USERNAME": "repo-username",
            "REPOSITORY_PASSWORD": "repo-password",
        },
    )
    mock_repository = mocker.patch.object(ArtifactRepo, "upload")
    mock_release = mocker.patch("semantic_release.cli.upload_to_release")
    mock_build_dists = mocker.patch("semantic_release.cli.build_dists")
    mock_remove_dists = mocker.patch("semantic_release.cli.remove_dists")
    mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("relekang", "python-semantic-release"),
    )
    mocker.patch("semantic_release.cli.evaluate_version_bump", lambda *x: "feature")
    mocker.patch("semantic_release.cli.generate_changelog")
    mocker.patch("semantic_release.cli.markdown_changelog", lambda *x, **y: "CHANGES")
    mocker.patch("semantic_release.cli.update_changelog_file")
    mocker.patch("semantic_release.cli.bump_version")
    mocker.patch("semantic_release.cli.get_new_version", lambda *x: "2.0.0")
    mocker.patch("semantic_release.cli.check_token", lambda: True)

    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            build_command="",
        ),
    )

    publish()

    assert mock_ci_check.called
    assert mock_push.called
    assert not mock_remove_dists.called
    assert not mock_build_dists.called
    assert mock_repository.called
    assert mock_release.called
    assert mock_should_bump_version.called
    mock_log.assert_called_once_with(
        "relekang", "python-semantic-release", "2.0.0", "CHANGES"
    )
    mock_checkout.assert_called_once_with("master")


def test_publish_retry_version_fail(mocker):
    mock_get_current = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="current"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    get_previous_release_version = mocker.patch(
        "semantic_release.cli.get_previous_release_version", return_value="previous"
    )
    mock_get_owner_name = mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mock_checkout = mocker.patch("semantic_release.cli.checkout")
    mocker.patch("semantic_release.cli.config.get", lambda *x: "my_branch")
    mock_should_bump_version = mocker.patch(
        "semantic_release.cli.should_bump_version", return_value=False
    )

    publish(noop=False, retry=True, force_level=False)

    mock_get_current.assert_called_once()
    mock_current_release_version.assert_called_once()
    get_previous_release_version.assert_called_once_with("current")
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with("my_branch")
    mock_should_bump_version.assert_called_once_with(
        current_version="previous",
        new_version="current",
        current_release_version="1.2.3",
        prerelease=False,
        noop=False,
        retry=True,
    )


def test_publish_bad_token(mocker):
    mock_get_current = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="current"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    get_previous_release_version = mocker.patch(
        "semantic_release.cli.get_previous_release_version", return_value="previous"
    )
    mock_get_owner_name = mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mock_checkout = mocker.patch("semantic_release.cli.checkout")
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            branch="my_branch",
            upload_to_repository=False,
            upload_to_release=False,
            remove_dist=False,
        ),
    )
    mock_should_bump_version = mocker.patch("semantic_release.cli.should_bump_version")
    mock_get_token = mocker.patch(
        "semantic_release.cli.get_token", return_value="SUPERTOKEN"
    )
    mock_get_domain = mocker.patch(
        "semantic_release.cli.get_domain", return_value="domain"
    )
    mock_push = mocker.patch("semantic_release.cli.push_new_version")
    mock_check_token = mocker.patch(
        "semantic_release.cli.check_token", return_value=False
    )

    publish(noop=False, retry=True, force_level=False)

    mock_get_current.assert_called_once()
    mock_current_release_version.assert_called_once()
    get_previous_release_version.assert_called_once_with("current")
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with("my_branch")
    mock_should_bump_version.assert_called_once_with(
        current_version="previous",
        new_version="current",
        current_release_version="1.2.3",
        prerelease=False,
        noop=False,
        retry=True,
    )
    mock_get_token.assert_called()
    mock_get_domain.assert_called()
    mock_push.assert_called_once_with(
        auth_token="SUPERTOKEN",
        owner="owner",
        name="name",
        branch="my_branch",
        domain="domain",
    )
    mock_check_token.assert_called_once_with()


def test_publish_giterror_when_posting(mocker):
    mock_current_version = mocker.patch(
        "semantic_release.cli.get_current_version", return_value="1.2.3"
    )
    mock_current_release_version = mocker.patch(
        "semantic_release.cli.get_current_release_version", return_value="1.2.3"
    )
    mock_evaluate = mocker.patch(
        "semantic_release.cli.evaluate_version_bump", return_value="patch"
    )
    mock_get_new = mocker.patch(
        "semantic_release.cli.get_new_version", return_value="new"
    )
    mock_get_owner_name = mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )
    mock_ci_check = mocker.patch("semantic_release.ci_checks.check")
    mock_checkout = mocker.patch("semantic_release.cli.checkout")
    mocker.patch(
        "semantic_release.cli.config.get",
        wrapped_config_get(
            branch="my_branch",
            upload_to_repository=False,
            upload_to_release=False,
            remove_dist=False,
        ),
    )
    mock_bump_version = mocker.patch("semantic_release.cli.bump_version")
    mock_should_bump_version = mocker.patch(
        "semantic_release.cli.should_bump_version", return_value=True
    )
    mock_get_token = mocker.patch(
        "semantic_release.cli.get_token", return_value="SUPERTOKEN"
    )
    mock_get_domain = mocker.patch(
        "semantic_release.cli.get_domain", return_value="domain"
    )
    mock_push = mocker.patch("semantic_release.cli.push_new_version")
    mock_check_token = mocker.patch(
        "semantic_release.cli.check_token", return_value=True
    )
    mock_generate = mocker.patch(
        "semantic_release.cli.generate_changelog", return_value="super changelog"
    )
    mock_markdown = mocker.patch(
        "semantic_release.cli.markdown_changelog", return_value="super md changelog"
    )
    mock_update_changelog_file = mocker.patch(
        "semantic_release.cli.update_changelog_file"
    )
    mock_post = mocker.patch(
        "semantic_release.cli.post_changelog", mock.Mock(side_effect=GitError())
    )

    publish(noop=False, retry=False, force_level=False)

    mock_current_version.assert_called_once()
    mock_current_release_version.assert_called_once()
    mock_evaluate.assert_called_once_with("1.2.3", False)
    mock_get_new.assert_called_once_with("1.2.3", "1.2.3", "patch", False, True)
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with("my_branch")
    mock_should_bump_version.assert_called_once_with(
        current_version="1.2.3",
        new_version="new",
        current_release_version="1.2.3",
        prerelease=False,
        noop=False,
        retry=False,
    )
    mock_update_changelog_file.assert_called_once_with("new", "super md changelog")
    mock_bump_version.assert_called_once_with("new", "patch")
    mock_get_token.assert_called_once_with()
    mock_get_domain.assert_called_once_with()
    mock_push.assert_called_once_with(
        auth_token="SUPERTOKEN",
        owner="owner",
        name="name",
        branch="my_branch",
        domain="domain",
    )
    mock_check_token.assert_called_once_with()
    mock_generate.assert_called_once_with("1.2.3")
    mock_markdown.assert_called_once_with(
        "owner",
        "name",
        "new",
        "super changelog",
        header=False,
        previous_version="1.2.3",
    )
    mock_post.assert_called_once_with("owner", "name", "new", "super md changelog")


def test_changelog_should_call_functions(mocker, runner):
    mock_changelog = mocker.patch("semantic_release.cli.changelog", return_value=True)
    result = runner.invoke(main, ["changelog"])
    assert result.exit_code == 0
    mock_changelog.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        prerelease=False,
        prerelease_patch=True,
        retry=False,
        unreleased=False,
        define=(),
    )


def test_overload_by_cli(mocker, runner):
    mock_read_text = mocker.patch(
        "semantic_release.history.Path.read_text", mock_version_file
    )
    runner.invoke(
        main,
        [
            "version",
            "--noop",
            "--patch",
            "-D",
            "version_variable=my_version_path:my_version_var",
        ],
    )

    mock_read_text.assert_called_once_with()
    mock_read_text.reset_mock()


def test_changelog_noop(mocker):
    mocker.patch("semantic_release.cli.get_current_version", return_value="current")
    mock_previous_version = mocker.patch(
        "semantic_release.cli.get_previous_version", return_value="previous"
    )
    mock_generate_changelog = mocker.patch(
        "semantic_release.cli.generate_changelog", return_value="super changelog"
    )
    mock_markdown_changelog = mocker.patch(
        "semantic_release.cli.markdown_changelog", return_value="super changelog"
    )
    mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )

    changelog(noop=True, unreleased=False)

    mock_previous_version.assert_called_once_with("current")
    mock_generate_changelog.assert_called_once_with("previous", "current")
    mock_markdown_changelog.assert_called_once_with(
        "owner", "name", "current", "super changelog", header=False
    )


def test_changelog_post_unreleased_no_token(mocker):
    mocker.patch("semantic_release.cli.get_current_version", return_value="current")
    mock_previous_version = mocker.patch(
        "semantic_release.cli.get_previous_version", return_value="previous"
    )
    mock_generate_changelog = mocker.patch(
        "semantic_release.cli.generate_changelog", return_value="super changelog"
    )
    mock_markdown_changelog = mocker.patch(
        "semantic_release.cli.markdown_changelog", return_value="super changelog"
    )
    mock_check_token = mocker.patch(
        "semantic_release.cli.check_token", return_value=False
    )
    mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )

    changelog(unreleased=True, post=True)

    mock_previous_version.assert_called_once_with("current")
    mock_generate_changelog.assert_called_once_with("current", None)
    mock_markdown_changelog.assert_called_once_with(
        "owner", "name", "current", "super changelog", header=False
    )
    mock_check_token.assert_called_once_with()


def test_changelog_post_complete(mocker):
    mocker.patch("semantic_release.cli.get_current_version", return_value="current")
    mock_previous_version = mocker.patch(
        "semantic_release.cli.get_previous_version", return_value="previous"
    )
    mock_generate_changelog = mocker.patch(
        "semantic_release.cli.generate_changelog", return_value="super changelog"
    )
    mock_markdown_changelog = mocker.patch(
        "semantic_release.cli.markdown_changelog", return_value="super md changelog"
    )
    mock_check_token = mocker.patch(
        "semantic_release.cli.check_token", return_value=True
    )
    mock_get_owner_name = mocker.patch(
        "semantic_release.cli.get_repository_owner_and_name",
        return_value=("owner", "name"),
    )
    mock_post_changelog = mocker.patch("semantic_release.cli.post_changelog")

    changelog(unreleased=True, post=True)

    mock_previous_version.assert_called_once_with("current")
    mock_generate_changelog.assert_called_once_with("current", None)
    mock_markdown_changelog.assert_any_call(
        "owner", "name", "current", "super changelog", header=False
    )
    mock_check_token.assert_called_once_with()
    mock_get_owner_name.assert_called_once_with()
    mock_post_changelog.assert_called_once_with(
        "owner", "name", "current", "super md changelog"
    )


def test_changelog_raises_exception_when_no_current_version(mocker):
    mocker.patch("semantic_release.cli.get_current_version", return_value=None)
    with pytest.raises(ImproperConfigurationError):
        changelog()
