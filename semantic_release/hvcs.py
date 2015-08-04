import requests

from .errors import ImproperConfigurationError
from .settings import config


class Github(object):

    @staticmethod
    def check_build_status(owner, repository, ref):
        url = 'https://api.github.com/repos/{owner}/{repo}/commits/{ref}/status'
        response = requests.get(url.format(owner=owner, repo=repository, ref=ref))
        return response.json()['state'] == 'success'


def get_hvcs():
    hvcs = config.get('semantic_release', 'hvcs')
    try:
        return globals()[hvcs.capitalize()]
    except KeyError:
        raise ImproperConfigurationError('"{0}" is not a valid option for hvcs.')


def check_build_status(owner, repository, ref):
    """
    Checks the build status of a commit on the api from your hosted version control provider.

    :param owner: The owner of the repository
    :param repository: The repository name
    :param ref: Commit or branch reference
    :return: A boolean with the build status
    """
    return get_hvcs().check_build_status(owner, repository, ref)
