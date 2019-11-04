import gitlab

from .. import mock

gitlab.Gitlab('')  # instanciation necessary to discover gitlab ProjectManager


class _GitlabProject:

    def __init__(self, status):
        self.commits = {'my_ref': self._Commit(status)}
        self.tags = self._Tags()

    class _Commit:

        def __init__(self, status):
            self.statuses = self._Statuses(status)

        class _Statuses:

            def __init__(self, status):
                if status == 'pending':
                    self.jobs = [
                        {'name': 'good_job', 'status': 'passed', 'allow_failure': False},
                        {'name': 'slow_job', 'status': 'pending', 'allow_failure': False},
                    ]
                elif status == 'failure':
                    self.jobs = [
                        {'name': 'good_job', 'status': 'passed', 'allow_failure': False},
                        {'name': 'bad_job', 'status': 'failed', 'allow_failure': False},
                    ]
                elif status == 'allow_failure':
                    self.jobs = [
                        {'name': 'notsobad_job', 'status': 'failed', 'allow_failure': True},
                        {'name': 'good_job2', 'status': 'passed', 'allow_failure': False},
                    ]
                elif status == 'success':
                    self.jobs = [
                        {'name': 'good_job1', 'status': 'passed', 'allow_failure': True},
                        {'name': 'good_job2', 'status': 'passed', 'allow_failure': False},
                    ]

            def list(self):
                return self.jobs

    class _Tags:

        def __init__(self):
            pass

        def get(self, version):
            if version == 'vmy_good_tag':
                return self._Tag()
            elif version == 'vmy_locked_tag':
                return self._Tag(locked=True)
            else:
                raise gitlab.exceptions.GitlabGetError

        class _Tag:

            def __init__(self, locked=False):
                self.locked = locked

            def set_release_description(self, changelog):
                if self.locked:
                    raise gitlab.exceptions.GitlabUpdateError


GITLAB_MOCKS = [
    mock.patch('os.environ', {'GL_TOKEN': 'token'}),
    mock.patch('configparser.ConfigParser.get', return_value='gitlab'),
    mock.patch('gitlab.Gitlab.auth'),
]


def mock_gitlab(status='success'):
    def wraps(func):
        for option in reversed(GITLAB_MOCKS):
            func = option(func)
        mock_project = mock.patch('gitlab.v4.objects.ProjectManager',
                                  return_value={'owner/repo': _GitlabProject(status)})
        return mock_project(func)
    return wraps
