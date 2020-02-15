"""HVCS
"""
import os
from typing import Optional

import gitlab
import ndebug
import requests

from .errors import ImproperConfigurationError
from .settings import config

debug = ndebug.create(__name__)
debug_gh = ndebug.create(__name__ + ':github')
debug_gl = ndebug.create(__name__ + ':gitlab')


class Base(object):

    @staticmethod
    def domain() -> str:
        raise NotImplementedError

    @staticmethod
    def token() -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        raise NotImplementedError

    @classmethod
    def post_release_changelog(
            cls, owner: str, repo: str, version: str, changelog: str) -> bool:
        raise NotImplementedError


class Github(Base):
    """Github helper class
    """
    API_URL = 'https://api.github.com'

    @staticmethod
    def domain() -> str:
        """Github domain property

        :return: The Github domain
        """
        return 'github.com'

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
            url.format(domain=Github.API_URL, owner=owner, repo=repo, ref=ref)
        )
        if debug_gh.enabled:
            debug_gh('check_build_status: state={}'.format(response.json()['state']))
        return response.json()['state'] == 'success'

    @classmethod
    def post_release_changelog(
            cls, owner: str, repo: str, version: str, changelog: str) -> bool:
        """Post release changelog

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version

        :return: The status of the request
        """
        url = '{domain}/repos/{owner}/{repo}/releases'
        tag = 'v{0}'.format(version)
        debug_gh('listing releases')
        response = requests.post(
            url.format(
                domain=Github.API_URL,
                owner=owner,
                repo=repo
            ),
            json={'tag_name': tag, 'body': changelog, 'draft': False, 'prerelease': False},
            headers={'Authorization': 'token {}'.format(Github.token())}
        )
        status, _ = response.status_code == 201, response.json()
        debug_gh('response #1, status_code={}, status={}'.format(response.status_code, status))

        if not status:
            debug_gh('not status, getting tag', tag)
            url = '{domain}/repos/{owner}/{repo}/releases/tags/{tag}'
            response = requests.get(
                url.format(
                    domain=Github.API_URL,
                    owner=owner,
                    repo=repo,
                    tag=tag
                ),
                headers={'Authorization': 'token {}'.format(Github.token())}
            )
            release_id = response.json()['id']
            debug_gh('response #2, status_code={}'.format(response.status_code))
            url = '{domain}/repos/{owner}/{repo}/releases/{id}'
            debug_gh('getting release_id', release_id)
            response = requests.post(
                url.format(
                    domain=Github.API_URL,
                    owner=owner,
                    repo=repo,
                    id=release_id
                ),
                json={'tag_name': tag, 'body': changelog, 'draft': False, 'prerelease': False},
                headers={'Authorization': 'token {}'.format(Github.token())}
            )
            status, _ = response.status_code == 200, response.json()
            debug_gh('response #3, status_code={}, status={}'.format(response.status_code, status))
        return status


class Gitlab(Base):
    """Gitlab helper class
    """
    API_URL = 'https://' + os.environ.get('CI_SERVER_HOST', 'gitlab.com')

    @staticmethod
    def domain() -> str:
        """Gitlab domain property

        :return: The Gitlab instance domain
        """
        return os.environ.get('CI_SERVER_HOST', 'gitlab.com')

    @staticmethod
    def token() -> Optional[str]:
        """Gitlab token property

        :return: The Gitlab token environment variable (GL_TOKEN) value
        """
        return os.environ.get('GL_TOKEN')

    @staticmethod
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        """Check last build status

        :param owner: The owner namespace of the repository. It includes all groups and subgroups.
        :param repo: The repository name
        :param ref: The sha1 hash of the commit ref

        :return: the status of the pipeline (False if a job failed)
        """
        gl = gitlab.Gitlab(Gitlab.API_URL, private_token=Gitlab.token())
        gl.auth()
        jobs = (gl.projects.get(owner+'/'+repo)
                  .commits.get(ref)
                  .statuses.list())
        for job in jobs:
            if job['status'] not in ['success', 'skipped']:
                if job['status'] == 'pending':
                    debug_gl('check_build_status: job {} is still in pending status'
                             .format(job['name']))
                    return False
                elif job['status'] == 'failed' and not job['allow_failure']:
                    debug_gl('check_build_status: job {} failed'
                             .format(job['name']))
                    return False
        return True

    @classmethod
    def post_release_changelog(
            cls, owner: str, repo: str, version: str, changelog: str) -> bool:
        """Post release changelog

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version

        :return: The status of the request
        """
        ref = 'v' + version
        gl = gitlab.Gitlab(Gitlab.API_URL, private_token=Gitlab.token())
        gl.auth()
        try:
            tag = gl.projects.get(owner+'/'+repo).tags.get(ref)
            tag.set_release_description(changelog)
        except gitlab.exceptions.GitlabGetError:
            debug_gl('Tag {} was not found for project {}'
                     .format(ref, owner+'/'+repo))
            return False
        except gitlab.exceptions.GitlabUpdateError:
            debug_gl('Failed to update tag {} for project {}'
                     .format(ref, owner+'/'+repo))
            return False

        return True


def get_hvcs() -> Base:
    """Get HVCS helper class

    :raises ImproperConfigurationError: if the hvcs option provided is not valid
    """
    hvcs = config.get('semantic_release', 'hvcs')
    debug('get_hvcs: hvcs=', hvcs)
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
    debug('check_build_status')
    return get_hvcs().check_build_status(owner, repository, ref)


def post_changelog(owner: str, repository: str, version: str, changelog: str) -> bool:
    """
    Posts the changelog to the current hvcs release API

    :param owner: The owner of the repository
    :param repository: The repository name
    :param version: A string with the new version
    :param changelog: A string with the changelog in correct format
    :return: a tuple with success status and payload from hvcs
    """
    debug('post_changelog(owner={}, repository={}, version={})'.format(owner, repository, version))
    return get_hvcs().post_release_changelog(owner, repository, version, changelog)


def get_token() -> Optional[str]:
    """
    Returns the token for the current VCS

    :return: The token in string form
    """
    return get_hvcs().token()


def get_domain() -> Optional[str]:
    """
    Returns the domain for the current VCS

    :return: The domain in string form
    """
    return get_hvcs().domain()


def check_token() -> bool:
    """
    Checks whether there exists a token or not.

    :return: A boolean telling if there is a token.
    """
    return get_hvcs().token() is not None
