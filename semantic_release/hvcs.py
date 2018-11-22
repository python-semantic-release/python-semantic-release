"""HVCS
"""
import os
from typing import Optional, Tuple

import requests

from .errors import ImproperConfigurationError
from .settings import config


class Base(object):

    @staticmethod
    def token() -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        raise NotImplementedError

    @classmethod
    def post_release_changelog(
            cls, owner: str, repo: str, version: str, changelog: str) -> Tuple[bool, dict]:
        raise NotImplementedError


class Github(Base):
    """Github helper class
    """
    DOMAIN = 'https://api.github.com'

    @staticmethod
    def token() -> Optional[str]:
        """Github token property

        :return: The Github token environment variable (GH_TOKEN) value
        """
        return os.environ.get('GH_TOKEN')

    @staticmethod
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        """Check build status

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param ref: The sha1 hash of the commit ref

        :return: Was the build status success?
        """
        url = '{domain}/repos/{owner}/{repo}/commits/{ref}/status'
        response = requests.get(
            url.format(domain=Github.DOMAIN, owner=owner, repo=repo, ref=ref)
        )
        return response.json()['state'] == 'success'

    @classmethod
    def post_release_changelog(
            cls, owner: str, repo: str, version: str, changelog: str) -> Tuple[bool, dict]:
        """Check build status

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version

        :return: The status of the request and the response json
        """
        url = '{domain}/repos/{owner}/{repo}/releases?access_token={token}'
        tag = 'v{0}'.format(version)
        response = requests.post(
            url.format(
                domain=Github.DOMAIN,
                owner=owner,
                repo=repo,
                token=Github.token()
            ),
            json={'tag_name': tag, 'body': changelog, 'draft': False, 'prerelease': False}
        )
        status, payload = response.status_code == 201, response.json()

        if not status:
            url = '{domain}/repos/{owner}/{repo}/releases/tags/{tag}?access_token={token}'
            response = requests.get(
                url.format(
                    domain=Github.DOMAIN,
                    owner=owner,
                    repo=repo,
                    token=Github().token(),
                    tag=tag
                ),
            )
            release_id = response.json()['id']
            url = '{domain}/repos/{owner}/{repo}/releases/{id}?access_token={token}'
            response = requests.post(
                url.format(
                    domain=Github.DOMAIN,
                    owner=owner,
                    repo=repo,
                    token=Github().token(),
                    id=release_id
                ),
                json={'tag_name': tag, 'body': changelog, 'draft': False, 'prerelease': False}
            )
            status, payload = response.status_code == 200, response.json()
        return status, payload


def get_hvcs() -> Base:
    """Get HVCS helper class

    :raises ImproperConfigurationError: if the hvcs option provided is not valid
    """
    hvcs = config.get('semantic_release', 'hvcs')
    try:
        return globals()[hvcs.capitalize()]
    except KeyError:
        raise ImproperConfigurationError('"{0}" is not a valid option for hvcs.')


def check_build_status(owner: str, repository: str, ref: str) -> bool:
    """
    Checks the build status of a commit on the api from your hosted version control provider.

    :param owner: The owner of the repository
    :param repository: The repository name
    :param ref: Commit or branch reference
    :return: A boolean with the build status
    """
    return get_hvcs().check_build_status(owner, repository, ref)


def post_changelog(owner: str, repository: str, version: str, changelog: str) -> Tuple[bool, dict]:
    """
    Posts the changelog to the current hvcs release API

    :param owner: The owner of the repository
    :param repository: The repository name
    :param version: A string with the new version
    :param changelog: A string with the changelog in correct format
    :return: a tuple with success status and payload from hvcs
    """
    return get_hvcs().post_release_changelog(owner, repository, version, changelog)


def check_token() -> bool:
    """
    Checks whether there exists a token or not.

    :return: A boolean telling if there is a token.
    """
    return get_hvcs().token() is not None
