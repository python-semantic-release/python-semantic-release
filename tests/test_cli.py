from click.testing import CliRunner

import semantic_release
from semantic_release.cli import changelog, main, publish, version
from semantic_release.errors import GitError, ImproperConfigurationError

from . import mock, pytest, reset_config
from .mocks import mock_version_file

assert reset_config


@pytest.fixture
def runner():
    return CliRunner()


def test_main_should_call_correct_function(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        retry=False,
        define=(),
    )
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

    def wrapped_config_get(*args, **kwargs):
        if (len(args) >= 2 and args[0] == 'semantic_release'
                and args[1] == 'version_source'):
            return 'tag'
        elif (len(args) >= 2 and args[0] == 'semantic_release'
                and args[1] == 'commit_version_number'):
            return True
        return orig(*args, **kwargs)

    mocker.patch('semantic_release.cli.config.get', wrapped_config_get)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    mock_set_new_version = mocker.patch('semantic_release.cli.set_new_version')
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mock_commit_new_version = mocker.patch('semantic_release.cli.commit_new_version')
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


def test_version_by_tag_with_commit_version_number_should_call_correct_functions(mocker, runner):
    orig = semantic_release.cli.config.get

    def wrapped_config_get(*args, **kwargs):
        if len(args) >= 2 and args[0] == 'semantic_release' and args[1] == 'version_source':
            return 'tag'
        return orig(*args, **kwargs)

    mocker.patch('semantic_release.cli.config.get', wrapped_config_get)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    mock_set_new_version = mocker.patch('semantic_release.cli.set_new_version')
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
    mock_set_new_version.assert_called_once_with('2.0.0')
    mock_tag_new_version.assert_called_once_with('2.0.0')
    assert result.exit_code == 0


def test_force_major(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--major'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level='major',
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]['force_level'] == 'major'
    assert result.exit_code == 0


def test_force_minor(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--minor'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level='minor',
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]['force_level'] == 'minor'
    assert result.exit_code == 0


def test_force_patch(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--patch'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level='patch',
        retry=False,
        define=(),
    )
    assert mock_version.call_args_list[0][1]['force_level'] == 'patch'
    assert result.exit_code == 0


def test_retry(mocker, runner):
    mock_version = mocker.patch('semantic_release.cli.version')
    result = runner.invoke(main, ['version', '--retry'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        retry=True,
        define=(),
    )
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

    def wrapped_config_get(*args, **kwargs):
        if len(args) >= 2 and args[0] == 'semantic_release' and args[1] == 'version_source':
            return 'tag'
        return orig(*args, **kwargs)

    mocker.patch('semantic_release.cli.config.get', wrapped_config_get)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: True)
    mock_check_build_status = mocker.patch('semantic_release.cli.check_build_status',
                                           return_value=True)
    mock_set_new_version = mocker.patch('semantic_release.cli.set_new_version')
    mock_tag_new_version = mocker.patch('semantic_release.cli.tag_new_version')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'major')
    result = runner.invoke(main, ['version'])
    assert mock_check_build_status.called
    assert mock_set_new_version.called
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


def test_version_retry_and_giterror(mocker):
    mocker.patch('semantic_release.cli.get_current_version',
                 mock.Mock(side_effect=GitError()))

    result = version(retry=True)

    assert not result


def test_version_retry(mocker):
    mock_get_current = mocker.patch('semantic_release.cli.get_current_version',
                                    return_value='current')
    mock_evaluate_bump = mocker.patch('semantic_release.cli.evaluate_version_bump',
                                      return_value='patch')
    mock_get_new = mocker.patch('semantic_release.cli.get_new_version',
                                return_value='new')
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)

    result = version(noop=False, retry=True, force_level=False)

    assert result
    mock_get_current.assert_called_once_with()
    mock_evaluate_bump.assert_called_once_with('current', False)
    mock_get_new.assert_called_once_with('current', 'patch')


def test_publish_should_not_upload_to_pypi_if_option_is_false(mocker, runner):
    mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.ci_checks.check')
    mock_upload_pypi = mocker.patch('semantic_release.cli.upload_to_pypi')
    mock_upload_release = mocker.patch('semantic_release.cli.upload_to_release')
    mocker.patch('semantic_release.cli.post_changelog', lambda *x: True)
    mocker.patch('semantic_release.cli.push_new_version', lambda *x: True)
    mocker.patch('semantic_release.cli.version', lambda: True)
    mocker.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.check_token', lambda: True)
    mocker.patch('semantic_release.cli.config.getboolean', lambda *x: False)
    runner.invoke(main, ['publish'])
    assert not mock_upload_pypi.called
    assert not mock_upload_release.called


def test_publish_should_do_nothing_when_version_fails(mocker, runner):
    mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'feature')
    mocker.patch('semantic_release.cli.generate_changelog')
    mock_log = mocker.patch('semantic_release.cli.post_changelog')
    mock_upload_pypi = mocker.patch('semantic_release.cli.upload_to_pypi')
    mock_upload_release = mocker.patch('semantic_release.cli.upload_to_release')
    mock_push = mocker.patch('semantic_release.cli.push_new_version')
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_version = mocker.patch('semantic_release.cli.version', return_value=False)
    result = runner.invoke(main, ['publish'])
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        retry=False,
        define=(),
    )
    assert not mock_push.called
    assert not mock_upload_pypi.called
    assert not mock_upload_release.called
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
    mock_release = mocker.patch('semantic_release.cli.upload_to_release')
    mock_build_dists = mocker.patch('semantic_release.cli.build_dists')
    mock_remove_dists = mocker.patch('semantic_release.cli.remove_dists')
    mocker.patch('semantic_release.cli.get_repository_owner_and_name',
                 return_value=('relekang', 'python-semantic-release'))
    mocker.patch('semantic_release.cli.evaluate_version_bump', lambda *x: 'feature')
    mocker.patch('semantic_release.cli.generate_changelog')
    mocker.patch('semantic_release.cli.markdown_changelog', lambda *x, **y: 'CHANGES')
    mocker.patch('semantic_release.cli.get_new_version', lambda *x: '2.0.0')
    mocker.patch('semantic_release.cli.check_token', lambda: True)

    result = runner.invoke(main, ['publish'])
    print(result.output)  # Print output for debugging should the test fail

    assert result.exit_code == 0
    assert mock_ci_check.called
    assert mock_push.called
    assert mock_remove_dists.called
    assert mock_build_dists.called
    assert mock_pypi.called
    assert mock_release.called
    mock_version.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        retry=False,
        define=(),
    )
    mock_log.assert_called_once_with(u'relekang', 'python-semantic-release', '2.0.0', 'CHANGES')
    mock_checkout.assert_called_once_with('master')


def test_publish_retry_version_fail(mocker):
    mock_get_current = mocker.patch('semantic_release.cli.get_current_version',
                                    return_value='current')
    mock_get_previous = mocker.patch('semantic_release.cli.get_previous_version',
                                     return_value='previous')
    mock_get_owner_name = mocker.patch('semantic_release.cli.get_repository_owner_and_name',
                                       return_value=('owner', 'name'))
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_checkout = mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.config.get', lambda *x: 'my_branch')
    mock_version = mocker.patch('semantic_release.cli.version', return_value=False)

    publish(noop=False, retry=True, force_level=False)

    mock_get_current.assert_called_once_with()
    mock_get_previous.assert_called_once_with('current')
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with('my_branch')
    mock_version.assert_called_once_with(noop=False, retry=True, force_level=False)


def test_publish_bad_token(mocker):
    mock_get_current = mocker.patch('semantic_release.cli.get_current_version',
                                    return_value='current')
    mock_get_previous = mocker.patch('semantic_release.cli.get_previous_version',
                                     return_value='previous')
    mock_get_owner_name = mocker.patch('semantic_release.cli.get_repository_owner_and_name',
                                       return_value=('owner', 'name'))
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_checkout = mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.config.get', return_value='my_branch')
    mocker.patch('semantic_release.cli.config.getboolean', return_value=False)
    mock_version = mocker.patch('semantic_release.cli.version')
    mock_get_token = mocker.patch('semantic_release.cli.get_token',
                                  return_value='SUPERTOKEN')
    mock_get_domain = mocker.patch('semantic_release.cli.get_domain',
                                   return_value='domain')
    mock_push = mocker.patch('semantic_release.cli.push_new_version')
    mock_check_token = mocker.patch('semantic_release.cli.check_token',
                                    return_value=False)

    publish(noop=False, retry=True, force_level=False)

    mock_get_current.assert_called_once_with()
    mock_get_previous.assert_called_once_with('current')
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with('my_branch')
    mock_version.assert_called_once_with(noop=False, retry=True, force_level=False)
    mock_get_token.assert_called()
    mock_get_domain.assert_called()
    mock_push.assert_called_once_with(auth_token='SUPERTOKEN', owner='owner', name='name',
                                      branch='my_branch', domain='domain')
    mock_check_token.assert_called_once_with()


def test_publish_giterror_when_posting(mocker):
    mock_get_current = mocker.patch('semantic_release.cli.get_current_version',
                                    return_value='current')
    mock_evaluate = mocker.patch('semantic_release.cli.evaluate_version_bump',
                                 return_value='patch')
    mock_get_new = mocker.patch('semantic_release.cli.get_new_version',
                                return_value='new')
    mock_get_owner_name = mocker.patch('semantic_release.cli.get_repository_owner_and_name',
                                       return_value=('owner', 'name'))
    mock_ci_check = mocker.patch('semantic_release.ci_checks.check')
    mock_checkout = mocker.patch('semantic_release.cli.checkout')
    mocker.patch('semantic_release.cli.config.get', return_value='my_branch')
    mocker.patch('semantic_release.cli.config.getboolean', return_value=False)
    mock_version = mocker.patch('semantic_release.cli.version')
    mock_get_token = mocker.patch('semantic_release.cli.get_token',
                                  return_value='SUPERTOKEN')
    mock_get_domain = mocker.patch('semantic_release.cli.get_domain',
                                   return_value='domain')
    mock_push = mocker.patch('semantic_release.cli.push_new_version')
    mock_check_token = mocker.patch('semantic_release.cli.check_token',
                                    return_value=True)
    mock_generate = mocker.patch('semantic_release.cli.generate_changelog',
                                 return_value='super changelog')
    mock_markdown = mocker.patch('semantic_release.cli.markdown_changelog',
                                 return_value='super md changelog')
    mock_post = mocker.patch('semantic_release.cli.post_changelog',
                             mock.Mock(side_effect=GitError()))

    publish(noop=False, retry=False, force_level=False)

    mock_get_current.assert_called_once_with()
    mock_evaluate.assert_called_once_with('current', False)
    mock_get_new.assert_called_once_with('current', 'patch')
    mock_get_owner_name.assert_called_once_with()
    mock_ci_check.assert_called()
    mock_checkout.assert_called_once_with('my_branch')
    mock_version.assert_called_once_with(noop=False, retry=False, force_level=False)
    mock_get_token.assert_called_once_with()
    mock_get_domain.assert_called_once_with()
    mock_push.assert_called_once_with(auth_token='SUPERTOKEN', owner='owner', name='name',
                                      branch='my_branch', domain='domain')
    mock_check_token.assert_called_once_with()
    mock_generate.assert_called_once_with('current', 'new')
    mock_markdown.assert_called_once_with('new', 'super changelog', header=False)
    mock_post.assert_called_once_with('owner', 'name', 'new', 'super md changelog')


def test_changelog_should_call_functions(mocker, runner):
    mock_changelog = mocker.patch('semantic_release.cli.changelog', return_value=True)
    result = runner.invoke(main, ['changelog'])
    assert result.exit_code == 0
    mock_changelog.assert_called_once_with(
        noop=False,
        post=False,
        force_level=None,
        retry=False,
        unreleased=False,
        define=(),
    )


def test_overload_by_cli(mocker, runner):
    mock_open = mocker.patch('semantic_release.history.open', mock_version_file)
    runner.invoke(main, ['version', '--noop', '--patch', '-D',
                         'version_variable=my_version_path:my_version_var'])

    mock_open.assert_called_once_with('my_version_path', 'r')
    mock_open.reset_mock()


def test_changelog_noop(mocker):
    mocker.patch('semantic_release.cli.get_current_version', return_value='current')
    mock_previous_version = mocker.patch('semantic_release.cli.get_previous_version',
                                         return_value='previous')
    mock_generate_changelog = mocker.patch('semantic_release.cli.generate_changelog',
                                           return_value='super changelog')
    mock_markdown_changelog = mocker.patch('semantic_release.cli.markdown_changelog',
                                           return_value='super changelog')

    changelog(noop=True, unreleased=False)

    mock_previous_version.assert_called_once_with('current')
    mock_generate_changelog.assert_called_once_with('previous', 'current')
    mock_markdown_changelog.assert_called_once_with('current', 'super changelog', header=False)


def test_changelog_post_unreleased_no_token(mocker):
    mocker.patch('semantic_release.cli.get_current_version', return_value='current')
    mock_previous_version = mocker.patch('semantic_release.cli.get_previous_version',
                                         return_value='previous')
    mock_generate_changelog = mocker.patch('semantic_release.cli.generate_changelog',
                                           return_value='super changelog')
    mock_markdown_changelog = mocker.patch('semantic_release.cli.markdown_changelog',
                                           return_value='super changelog')
    mock_check_token = mocker.patch('semantic_release.cli.check_token',
                                    return_value=False)

    changelog(unreleased=True, post=True)

    mock_previous_version.assert_called_once_with('current')
    mock_generate_changelog.assert_called_once_with('current', None)
    mock_markdown_changelog.assert_called_once_with('current', 'super changelog', header=False)
    mock_check_token.assert_called_once_with()


def test_changelog_post_complete(mocker):
    mocker.patch('semantic_release.cli.get_current_version', return_value='current')
    mock_previous_version = mocker.patch('semantic_release.cli.get_previous_version',
                                         return_value='previous')
    mock_generate_changelog = mocker.patch('semantic_release.cli.generate_changelog',
                                           return_value='super changelog')
    mock_markdown_changelog = mocker.patch('semantic_release.cli.markdown_changelog',
                                           return_value='super md changelog')
    mock_check_token = mocker.patch('semantic_release.cli.check_token',
                                    return_value=True)
    mock_get_owner_name = mocker.patch('semantic_release.cli.get_repository_owner_and_name',
                                       return_value=('owner', 'name'))
    mock_post_changelog = mocker.patch('semantic_release.cli.post_changelog')

    changelog(unreleased=True, post=True)

    mock_previous_version.assert_called_once_with('current')
    mock_generate_changelog.assert_called_once_with('current', None)
    mock_markdown_changelog.assert_any_call('current', 'super changelog', header=False)
    mock_check_token.assert_called_once_with()
    mock_get_owner_name.assert_called_once_with()
    mock_post_changelog.assert_called_once_with('owner', 'name', 'current',
                                                'super md changelog')


def test_changelog_raises_exception_when_no_current_version(mocker):
    mocker.patch('semantic_release.cli.get_current_version', return_value=None)
    with pytest.raises(ImproperConfigurationError):
        changelog()


@mock.patch('semantic_release.cli.debug')
def test_main_debug(mock_debug, runner):
    runner.invoke(main, ['version', '--noop'])
    assert mock_debug.called
