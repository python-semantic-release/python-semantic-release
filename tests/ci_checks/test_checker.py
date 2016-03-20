from semantic_release import ci_checks


def test_check_should_call_travis_with_correct_env_variable(mocker, monkeypatch):
    mock_travis = mocker.patch('semantic_release.ci_checks.travis')
    monkeypatch.setenv('TRAVIS', 'true')
    ci_checks.check('master')
    mock_travis.assert_called_once_with('master')


def test_check_should_call_semaphore_with_correct_env_variable(mocker, monkeypatch):
    mock_semaphore = mocker.patch('semantic_release.ci_checks.semaphore')
    monkeypatch.setenv('SEMAPHORE', 'true')
    ci_checks.check('master')
    mock_semaphore.assert_called_once_with('master')


def test_check_should_call_frigg_with_correct_env_variable(mocker, monkeypatch):
    mock_frigg = mocker.patch('semantic_release.ci_checks.frigg')
    monkeypatch.setenv('FRIGG', 'true')
    ci_checks.check('master')
    mock_frigg.assert_called_once_with('master')
