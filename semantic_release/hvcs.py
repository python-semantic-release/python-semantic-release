"""HVCS
"""
import logging
import mimetypes
import os
from typing import Optional, Union

from gitlab import exceptions, gitlab
from requests import HTTPError, Session
from requests.auth import AuthBase
from urllib3 import Retry

from .errors import ImproperConfigurationError
from .helpers import LoggedFunction, build_requests_session
from .settings import config

logger = logging.getLogger(__name__)

# Add a mime type for wheels
mimetypes.add_type("application/octet-stream", ".whl")


class Base(object):
    @staticmethod
    def domain() -> str:
        raise NotImplementedError

    @staticmethod
    def api_url() -> str:
        raise NotImplementedError

    @staticmethod
    def token() -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        raise NotImplementedError

    @classmethod
    def post_release_changelog(
        cls, owner: str, repo: str, version: str, changelog: str
    ) -> bool:
        raise NotImplementedError

    @classmethod
    def upload_dists(cls, owner: str, repo: str, version: str, path: str) -> bool:
        # Skip on unsupported HVCS instead of raising error
        return True


def _fix_mime_types():
    """Fix incorrect entries in the `mimetypes` registry.
    On Windows, the Python standard library's `mimetypes` reads in
    mappings from file extension to MIME type from the Windows
    registry. Other applications can and do write incorrect values
    to this registry, which causes `mimetypes.guess_type` to return
    incorrect values, which causes TensorBoard to fail to render on
    the frontend.
    This method hard-codes the correct mappings for certain MIME
    types that are known to be either used by python-semantic-release or
    problematic in general.
    """
    mimetypes.add_type("text/markdown", ".md")


class TokenAuth(AuthBase):
    """
    requests Authentication for token based authorization
    """

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return all(
            [
                self.token == getattr(other, "token", None),
            ]
        )

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers["Authorization"] = f"token {self.token}"
        return r


class Github(Base):
    """Github helper class"""

    DEFAULT_DOMAIN = "github.com"
    _fix_mime_types()

    @staticmethod
    def domain() -> str:
        """Github domain property

        :return: The Github domain
        """
        hvcs_domain = config.get("hvcs_domain")
        domain = hvcs_domain if hvcs_domain else Github.DEFAULT_DOMAIN
        return domain

    @staticmethod
    def api_url() -> str:
        """Github api_url property

        :return: The Github API URL
        """
        # not necessarily prefixed with api in the case of a custom domain, so
        # can't just default DEFAULT_DOMAIN to github.com
        hvcs_domain = config.get("hvcs_domain")
        hostname = hvcs_domain if hvcs_domain else "api." + Github.DEFAULT_DOMAIN
        return f"https://{hostname}"

    @staticmethod
    def token() -> Optional[str]:
        """Github token property

        :return: The Github token environment variable (GH_TOKEN) value
        """
        return os.environ.get("GH_TOKEN")

    @staticmethod
    def auth() -> Optional[TokenAuth]:
        """Github token property

        :return: The Github token environment variable (GH_TOKEN) value
        """
        token = Github.token()
        if not token:
            return None
        return TokenAuth(token)

    @staticmethod
    def session(
        raise_for_status=True, retry: Union[Retry, bool, int] = True
    ) -> Session:
        session = build_requests_session(raise_for_status=raise_for_status, retry=retry)
        session.auth = Github.auth()
        return session

    @staticmethod
    @LoggedFunction(logger)
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        """Check build status

        https://docs.github.com/rest/reference/repos#get-the-combined-status-for-a-specific-reference

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param ref: The sha1 hash of the commit ref

        :return: Was the build status success?
        """
        url = "{domain}/repos/{owner}/{repo}/commits/{ref}/status"
        try:
            response = Github.session().get(
                url.format(domain=Github.api_url(), owner=owner, repo=repo, ref=ref)
            )
            return response.json().get("state") == "success"
        except HTTPError as e:
            logger.warning(f"Build status check on Github has failed: {e}")
            return False

    @classmethod
    @LoggedFunction(logger)
    def create_release(cls, owner: str, repo: str, tag: str, changelog: str) -> bool:
        """Create a new release

        https://docs.github.com/rest/reference/repos#create-a-release

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param tag: Tag to create release for
        :param changelog: The release notes for this version

        :return: Whether the request succeeded
        """
        try:
            Github.session().post(
                f"{Github.api_url()}/repos/{owner}/{repo}/releases",
                json={
                    "tag_name": tag,
                    "name": tag,
                    "body": changelog,
                    "draft": False,
                    "prerelease": False,
                },
            )
            return True
        except HTTPError as e:
            logger.warning(f"Release creation on Github has failed: {e}")
            return False

    @classmethod
    @LoggedFunction(logger)
    def get_release(cls, owner: str, repo: str, tag: str) -> Optional[int]:
        """Get a release by its tag name

        https://docs.github.com/rest/reference/repos#get-a-release-by-tag-name

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param tag: Tag to get release for

        :return: ID of found release
        """
        try:
            response = Github.session().get(
                f"{Github.api_url()}/repos/{owner}/{repo}/releases/tags/{tag}"
            )
            return response.json().get("id")
        except HTTPError as e:
            if e.response.status_code != 404:
                logger.debug(f"Get release by tag on Github has failed: {e}")
            return None

    @classmethod
    @LoggedFunction(logger)
    def edit_release(cls, owner: str, repo: str, id: int, changelog: str) -> bool:
        """Edit a release with updated change notes

        https://docs.github.com/rest/reference/repos#update-a-release

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param id: ID of release to update
        :param changelog: The release notes for this version

        :return: Whether the request succeeded
        """
        try:
            Github.session().post(
                f"{Github.api_url()}/repos/{owner}/{repo}/releases/{id}",
                json={"body": changelog},
            )
            return True
        except HTTPError as e:
            logger.warning(f"Edit release on Github has failed: {e}")
            return False

    @classmethod
    @LoggedFunction(logger)
    def post_release_changelog(
        cls, owner: str, repo: str, version: str, changelog: str
    ) -> bool:
        """Post release changelog

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version

        :return: The status of the request
        """
        tag = f"v{version}"
        logger.debug(f"Attempting to create release for {tag}")
        success = Github.create_release(owner, repo, tag, changelog)

        if not success:
            logger.debug("Unsuccessful, looking for an existing release to update")
            release_id = Github.get_release(owner, repo, tag)
            if release_id:
                logger.debug(f"Updating release {release_id}")
                success = Github.edit_release(owner, repo, release_id, changelog)
            else:
                logger.debug(f"Existing release not found")

        return success

    @classmethod
    @LoggedFunction(logger)
    def upload_asset(
        cls, owner: str, repo: str, release_id: int, file: str, label: str = None
    ) -> bool:
        """Upload an asset to an existing release

        https://docs.github.com/rest/reference/repos#upload-a-release-asset

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param release_id: ID of the release to upload to
        :param file: Path of the file to upload
        :param label: Custom label for this file

        :return: The status of the request
        """
        url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"

        content_type = mimetypes.guess_type(file, strict=False)[0]
        if not content_type:
            content_type = "application/octet-stream"

        try:
            response = Github.session().post(
                url,
                params={"name": os.path.basename(file), "label": label},
                headers={
                    "Content-Type": content_type,
                },
                data=open(file, "rb").read(),
            )

            logger.debug(
                f"Asset upload on Github completed, url: {response.url}, status code: {response.status_code}"
            )

            return True
        except HTTPError as e:
            logger.warning(f"Asset upload {file} on Github has failed: {e}")
            return False

    @classmethod
    def upload_dists(cls, owner: str, repo: str, version: str, path: str) -> bool:
        """Upload distributions to a release

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: Version to upload for
        :param path: Path to the dist directory

        :return: The status of the request
        """

        # Find the release corresponding to this version
        release_id = Github.get_release(owner, repo, f"v{version}")
        if not release_id:
            logger.debug("No release found to upload assets to")
            return False

        # Upload assets
        one_or_more_failed = False
        for file in os.listdir(path):
            file_path = os.path.join(path, file)

            if not Github.upload_asset(owner, repo, release_id, file_path):
                one_or_more_failed = True

        return not one_or_more_failed


class Gitlab(Base):
    """Gitlab helper class"""

    @staticmethod
    def domain() -> str:
        """Gitlab domain property

        :return: The Gitlab instance domain
        """
        domain = config.get("hvcs_domain", os.environ.get("CI_SERVER_HOST"))
        return domain if domain else "gitlab.com"

    @staticmethod
    def api_url() -> str:
        """Gitlab api_url property

        :return: The Gitlab instance API url
        """
        return f"https://{Gitlab.domain()}"

    @staticmethod
    def token() -> Optional[str]:
        """Gitlab token property

        :return: The Gitlab token environment variable (GL_TOKEN) value
        """
        return os.environ.get("GL_TOKEN")

    @staticmethod
    @LoggedFunction(logger)
    def check_build_status(owner: str, repo: str, ref: str) -> bool:
        """Check last build status

        :param owner: The owner namespace of the repository. It includes all groups and subgroups.
        :param repo: The repository name
        :param ref: The sha1 hash of the commit ref

        :return: the status of the pipeline (False if a job failed)
        """
        gl = gitlab.Gitlab(Gitlab.api_url(), private_token=Gitlab.token())
        gl.auth()
        jobs = gl.projects.get(owner + "/" + repo).commits.get(ref).statuses.list()
        for job in jobs:
            if job["status"] not in ["success", "skipped"]:
                if job["status"] == "pending":
                    logger.debug(
                        f"check_build_status: job {job['name']} is still in pending status"
                    )
                    return False
                elif job["status"] == "failed" and not job["allow_failure"]:
                    logger.debug(f"check_build_status: job {job['name']} failed")
                    return False
        return True

    @classmethod
    @LoggedFunction(logger)
    def post_release_changelog(
        cls, owner: str, repo: str, version: str, changelog: str
    ) -> bool:
        """Post release changelog

        :param owner: The owner namespace of the repository
        :param repo: The repository name
        :param version: The version number
        :param changelog: The release notes for this version

        :return: The status of the request
        """
        ref = "v" + version
        gl = gitlab.Gitlab(Gitlab.api_url(), private_token=Gitlab.token())
        gl.auth()
        try:
            gl.projects.get(owner + "/" + repo).releases.create(
                {
                    "name": "Release " + version,
                    "tag_name": ref,
                    "description": changelog,
                }
            )
        except exceptions.GitlabCreateError:
            logger.debug(
                f"Release {ref} could not be created for project {owner}/{repo}"
            )
            return False

        return True


@LoggedFunction(logger)
def get_hvcs() -> Base:
    """Get HVCS helper class

    :raises ImproperConfigurationError: if the hvcs option provided is not valid
    """
    hvcs = config.get("hvcs")
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
    logger.debug(f"Checking build status for {owner}/{repository}#{ref}")
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
    logger.debug(f"Posting release changelog for {owner}/{repository} {version}")
    return get_hvcs().post_release_changelog(owner, repository, version, changelog)


def upload_to_release(owner: str, repository: str, version: str, path: str) -> bool:
    """
    Upload distributions to the current hvcs release API

    :param owner: The owner of the repository
    :param repository: The repository name
    :param version: A string with the version to upload for
    :param path: Path to dist directory

    :return: Status of the request
    """

    return get_hvcs().upload_dists(owner, repository, version, path)


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
