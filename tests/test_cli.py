import pytest
from click.testing import CliRunner

import semantic_release
from semantic_release.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_main_should_call_correct_function(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version'])
    mock_version.assert_called_once_with(
        noop=False, post=False, force_level=None)
    assert result.exit_code == 0


def test_version_by_commit_should_call_correct_functions(mocker, runner):
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_commit_new_version = mocker.patch('semantic_release.cli.commit_new_version')
    mock_set_new_version = mocker.patch('semantic_release.cli.set_new_version')
    mock_new_version = mocker.patch('semantic_release.cli.get_new_version', return_value='2.0.0')
    mock_evaluate_bump = mocker.patch('semantic_release.cli.evaluate_version_bump',
                                      return_value='major')
    mock_current_version = mocker.patch('semantic_release.cli.get_current_version',
                                        return_value='1.2.3')

    result = runner.invoke(main, ['version'])
    mock_current_version.assert_called_once_with()
    mock_evaluate_bump.assert_called_once_with('1.2.3', None)
    mock_new_version.assert_called_once_with('1.2.3', 'major')
    mock_set_new_version.assert_called_once_with('2.0.0')
    mock_commit_new_version.assert_called_once_with('2.0.0')
    mock_tag_new_version.assert_called_once_with('2.0.0')
    assert result.exit_code == 0


def test_version_by_tag_should_call_correct_functions(mocker, runner):
    orig = semantic_release.cli.config.get

    def wrapped_config_get(*args):
        if len(args) >= 2 and args[0] == 'semantic_release' and args[1] == 'version_source':
            return 'tag'
        return orig(*args)

    mocker.patch('semantic_release.cli.config.get', wrapped_config_get)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_new_version = mocker.patch('semantic_release.cli.get_new_version', return_value='2.0.0')
    mock_evaluate_bump = mocker.patch('semantic_release.cli.evaluate_version_bump',
                                      return_value='major')
    mock_current_version = mocker.patch('semantic_release.cli.get_current_version',
                                        return_value='1.2.3')
    result = runner.invoke(main, ['version'])
    mock_current_version.assert_called_once_with()
    mock_evaluate_bump.assert_called_once_with('1.2.3', None)
    mock_new_version.assert_called_once_with('1.2.3', 'major')
    mock_tag_new_version.assert_called_once_with('2.0.0')
    assert result.exit_code == 0


def test_force_major(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--major'])
    mock_version.assert_called_once_with(noop=False, post=False, force_level='major')
    assert mock_version.call_args_list[0][1]['force_level'] == 'major'
    assert result.exit_code == 0


def test_force_minor(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--minor'])
    mock_version.assert_called_once_with(
        noop=False, post=False, force_level='minor')
    assert mock_version.call_args_list[0][1]['force_level'] == 'minor'
    assert result.exit_code == 0


def test_force_patch(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--patch'])
    mock_version.assert_called_once_with(noop=False, post=False, force_level='patch')
    assert mock_version.call_args_list[0][1]['force_level'] == 'patch'
    assert result.exit_code == 0


def test_noop_mode(mocker, runner):
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_set_new = mocker.patch('semantic_release.cli.commit_new_version')
    mock_commit_new = mocker.patch('semantic_release.cli.set_new_version')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    result = runner.invoke(main, ['version', '--noop'])
    assert not mock_set_new.called
    assert not mock_commit_new.called
    assert not mock_tag_new_version.called
    assert result.exit_code == 0


def test_version_no_change(mocker, runner):
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_commit_new_version = mocker.patch('semantic_release.cli.commit_new_version')
    mock_set_new_version = mocker.patch('semantic_release.cli.set_new_version')
    mock_new_version = mocker.patch('semantic_release.cli.get_new_version', return_value='1.2.3')
    mock_evaluate_bump = mocker.patch('semantic_release.cli.evaluate_version_bump',
                                      return_value=None)
    mock_current_version = mocker.patch('semantic_release.cli.get_current_version',
                                        return_value='1.2.3')
    result = runner.invoke(main, ['version'])
    mock_current_version.assert_called_once_with()
    mock_evaluate_bump.assert_called_once_with('1.2.3', None)
    mock_new_version.assert_called_once_with('1.2.3', None)
    assert not mock_set_new_version.called
    assert not mock_commit_new_version.called
    assert not mock_tag_new_version.called
    assert result.exit_code == 0


def test_version_check_build_status_fails(mocker, runner):
    mock_check_build_status = mocker.patch('semantic_release.cli.check_build_status',
                                           return_value=False)
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_commit_new = mocker.patch('semantic_release.cli.commit_new_version')
    mock_set_new = mocker.patch('semantic_release.cli.set_new_version')
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    result = runner.invoke(main, ['version'])
    assert mock_check_build_status.called
    assert not mock_set_new.called
    assert not mock_commit_new.called
    assert not mock_tag_new_version.called
    assert result.exit_code == 0


def test_version_by_commit_check_build_status_succeeds(mocker, runner):
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    mock_check_build_status = mocker.patch('semantic_release.cli.check_build_status',
                                           return_value=True)
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    mock_commit_new = mocker.patch('semantic_release.cli.commit_new_version')
    mock_set_new = mocker.patch('semantic_release.cli.set_new_version')
    result = runner.invoke(main, ['version'])
    assert mock_check_build_status.called
    assert mock_set_new.called
    assert mock_commit_new.called
    assert mock_tag_new_version.called
    assert result.exit_code == 0


def test_version_by_tag_check_build_status_succeeds(mocker, runner):
    orig = semantic_release.cli.config.get

    def wrapped_config_get(*args):
        print(args)
        if len(args) >= 2 and args[0] == 'semantic_release' and args[1] == 'version_source':
            return 'tag'
        return orig(*args)

    mocker.patch('semantic_release.cli.config.get', wrapped_config_get)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    mock_check_build_status = mocker.patch('semantic_release.cli.check_build_status',
                                           return_value=True)
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    result = runner.invoke(main, ['version'])
    assert mock_check_build_status.called
    assert mock_tag_new_version.called
    assert result.exit_code == 0


def test_version_check_build_status_not_called_if_disabled(mocker, runner):
    mock_check_build_status = mocker.patch('semantic_release.cli.check_build_status')
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    mocker.patch('semantic_release.cli.tag_new_version', None)
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    mocker.patch('semantic_release.cli.commit_new_version', None)
    mocker.patch('semantic_release.cli.set_new_version', None)
    runner.invoke(main, ['version'])
    assert not mock_check_build_status.called


def test_publish_should_not_upload_to_pypi_if_option_is_false(mocker, runner):
    mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.ci_checks.check')
    mock_upload = mocker.patch('semantic_release.cli.upload_to_pypi')
    mocker.patch('semantic_release.cli.post_changelog', lambda *x: True)
    mocker.patch('semantic_release.cli.push_new_version', lambda *x: True)
    mocker.patch('semantic_release.cli.version', lambda: True)
    mocker.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.check_token', lambda: True)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    runner.invoke(main, ['publish'])
    assert not mock_upload.called


def test_publish_should_do_nothing_when_version_fails(mocker, runner):
    mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'feature')
    mocker.patch('semantic_release.cli.generate_changelog')
    mock_log = mocker.patch('semantic_release.cli.post_changelog')
    mock_upload = mocker.patch('semantic_release.cli.upload_to_pypi')
    mock_push = mocker.patch('semantic_release.cli.push_new_version')
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_version = mocker.patch('semantic_release.cli.version', return_value=False)
    result = runner.invoke(main, ['publish'])
    mock_version.assert_called_once_with(
        noop=False, post=False, force_level=None)
    assert not mock_push.called
    assert not mock_upload.called
    assert not mock_log.called
    assert mock_ci_check.called
    assert result.exit_code == 0


def test_publish_should_call_functions(mocker, runner):
    mock_push = mocker.patch('semantic_release.cli.push_new_version')
    mock_checkout = mocker.patch('semantic_release.cli.checkout')
    mock_version = mocker.patch('semantic_release.cli.version', return_value=True)
    mock_log = mocker.patch('semantic_release.cli.post_changelog')
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_pypi = mocker.patch('semantic_release.cli.upload_to_pypi')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'feature')
    mocker.patch('semantic_release.cli.generate_changelog')
    mocker.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.check_token', lambda: True)
    result = runner.invoke(main, ['publish'])
    assert result.exit_code == 0
    assert mock_ci_check.called
    assert mock_push.called
    assert mock_pypi.called
    mock_version.assert_called_once_with(noop=False, post=False, force_level=None)
    mock_log.assert_called_once_with(u'relekang', 'python-semantic-release', '2.0.0', 'CHANGES')
    mock_checkout.assert_called_once_with('master')


def test_changelog_should_call_functions(mocker, runner):
    mock_changelog = mocker.patch('semantic_release.cli.changelog', return_value=True)
    result = runner.invoke(main, ['changelog'])
    assert result.exit_code == 0
    mock_changelog.assert_called_once_with(noop=False, post=False, force_level=None)
