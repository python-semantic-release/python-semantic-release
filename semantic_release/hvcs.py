import os

import requests

from .errors import ImproperConfigurationError
from .settings import config


class Github(object):

    @staticmethod
    def token():
        return os.environ.get('GH_TOKEN')

    @staticmethod
    def check_build_status(owner, repository, ref):
        url = 'https://api.github.com/repos/{owner}/{repo}/commits/{ref}/status'
        response = requests.get(url.format(owner=owner, repo=repository, ref=ref))
        return response.json()['state'] == 'success'

    @classmethod
    def post_release_changelog(cls, owner, repository, version, changelog):
        url = 'https://api.github.com/repos/{owner}/{repo}/releases?access_token={token}'
        tag = 'v{0}'.format(version)
        response = requests.post(
            url.format(owner=owner, repo=repository, token=Github.token()),
            json={'tag_name': tag, 'body': changelog, 'draft': False, 'prerelease': False}
        )
        return response.status_code == 201, response.json()


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


def post_changelog(owner, repository, version, changelog):
    """
    Posts the changelog to the current hcvs release API

    :param owner: The owner of the repository
    :param repository: The repository name
    :param version: A string with the new version
    :param changelog: A string with the changelog in correct format
    :return: a tuple with successtatus and payload from hvcs
    """
    return get_hvcs().post_release_changelog(owner, repository, version, changelog)


def check_token():
    return get_hvcs().token() is not None
