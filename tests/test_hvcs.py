import json
import os
from unittest import TestCase

import pytest
import responses

from semantic_release.errors import ImproperConfigurationError
from semantic_release.hvcs import (Github, Gitlab, check_build_status, check_token, get_hvcs,
                                   post_changelog)

from . import mock
from .mocks.mock_gitlab import mock_gitlab


@mock.patch('configparser.ConfigParser.get', return_value='github')
def test_get_hvcs_should_return_github(mock_get_vcs):
    assert(get_hvcs() == Github)


@mock.patch('configparser.ConfigParser.get', return_value='gitlab')
def test_get_hvcs_should_return_gitlab(mock_get_vcs):
    assert(get_hvcs() == Gitlab)


@mock.patch('semantic_release.hvcs.config.get', lambda *x: 'doesnotexist')
def test_get_hvcs_should_raise_improper_config():
    pytest.raises(ImproperConfigurationError, get_hvcs)


@mock.patch('semantic_release.hvcs.Github.check_build_status')
def test_check_build_status(mock_github_helper):
    check_build_status('owner', 'name', 'ref')
    mock_github_helper.assert_called_once_with('owner', 'name', 'ref')


@mock.patch('os.environ', {'GH_TOKEN': 'token'})
def test_check_token_should_return_true():
    assert(check_token() is True)


@mock.patch('os.environ', {})
def test_check_token_should_return_false():
    assert(check_token() is False)


@mock.patch('configparser.ConfigParser.get', return_value='gitlab')
@mock.patch('os.environ', {'GL_TOKEN': 'token'})
def test_get_domain_and_token(mock_get_vcs):
    assert(get_hvcs().domain())
    assert(get_hvcs().token())


class GithubCheckBuildStatusTests(TestCase):
    url = ('https://api.github.com/repos/relekang/rmoq/commits/'
           '6dcb09b5b57875f334f61aebed695e2e4193db5e/status')

    def get_response(self, status):
        return json.dumps({
            "state": status,
            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            "total_count": 2,
        })

    @responses.activate
    def test_should_return_false_if_pending(self):
        responses.add(
            responses.GET,
            self.url,
            body=self.get_response('pending'),
            content_type='application/json'
        )
        self.assertFalse(Github.check_build_status('relekang', 'rmoq',
                                                   '6dcb09b5b57875f334f61aebed695e2e4193db5e'))

    @responses.activate
    def test_should_return_false_if_failure(self):
        responses.add(
            responses.GET,
            self.url,
            body=self.get_response('failure'),
            content_type='application/json'
        )
        self.assertFalse(Github.check_build_status('relekang', 'rmoq',
                                                   '6dcb09b5b57875f334f61aebed695e2e4193db5e'))

    @responses.activate
    def test_should_return_true_if_success(self):
        responses.add(
            responses.GET,
            self.url,
            body=self.get_response('success'),
            content_type='application/json'
        )
        self.assertTrue(Github.check_build_status('relekang', 'rmoq',
                                                  '6dcb09b5b57875f334f61aebed695e2e4193db5e'))


class GitlabCheckBuildStatusTests(TestCase):

    @mock_gitlab('pending')
    def test_should_return_false_if_pending(self, mock_config, mock_auth, mock_project):
        self.assertFalse(check_build_status('owner', 'repo', 'my_ref'))

    @mock_gitlab('failure')
    def test_should_return_false_if_failure(self, mock_config, mock_auth, mock_project):
        self.assertFalse(check_build_status('owner', 'repo', 'my_ref'))

    @mock_gitlab('allow_failure')
    def test_should_return_true_if_allow_failure(self, mock_config, mock_auth, mock_project):
        self.assertTrue(check_build_status('owner', 'repo', 'my_ref'))

    @mock_gitlab('success')
    def test_should_return_true_if_success(self, mock_config, mock_auth, mock_project):
        self.assertTrue(check_build_status('owner', 'repo', 'my_ref'))


class GithubReleaseTests(TestCase):
    url = 'https://api.github.com/repos/relekang/rmoq/releases'
    edit_url = 'https://api.github.com/repos/relekang/rmoq/releases/1'
    get_url = 'https://api.github.com/repos/relekang/rmoq/releases/tags/v1.0.0'
    asset_url = 'https://uploads.github.com/repos/relekang/rmoq/releases/1/assets'
    asset_url_params = ('https://uploads.github.com/repos/relekang/rmoq/releases/1/assets'
                        '?name=testupload.md&label=Dummy+file')
    dist_asset_url_params = ('https://uploads.github.com/repos/relekang/rmoq/releases/1/assets'
                             '?name=testupload.md')

    @responses.activate
    @mock.patch('semantic_release.hvcs.Github.token', return_value='super-token')
    def test_should_post_changelog(self, mock_token):
        def request_callback(request):
            payload = json.loads(request.body)
            self.assertEqual(payload['tag_name'], 'v1.0.0')
            self.assertEqual(payload['body'], 'text')
            self.assertEqual(payload['draft'], False)
            self.assertEqual(payload['prerelease'], False)
            self.assertEqual('token super-token', request.headers['Authorization'])

            return 201, {}, json.dumps({})

        responses.add_callback(
            responses.POST,
            self.url,
            callback=request_callback,
            content_type='application/json'
        )
        status = Github.post_release_changelog('relekang', 'rmoq', '1.0.0', 'text')
        self.assertTrue(status)

    @responses.activate
    def test_should_return_false_status_if_it_failed(self):
        responses.add(
            responses.POST,
            self.url,
            status=400,
            body='{}',
            content_type='application/json'
        )
        responses.add(
            responses.GET,
            self.get_url,
            status=200,
            body='{"id": 1}',
            content_type='application/json'
        )
        responses.add(
            responses.POST,
            self.edit_url,
            status=400,
            body='{}',
            content_type='application/json'
        )
        self.assertFalse(Github.post_release_changelog('relekang', 'rmoq', '1.0.0', 'text'))

    @responses.activate
    @mock.patch('semantic_release.hvcs.Github.token', return_value='super-token')
    def test_should_upload_asset(self, mock_token):
        # Create temporary file to upload
        dummy_file_path = '/tmp/testupload.md'
        dummy_content = '# Test File\n\n*Dummy asset for testing uploads.*'
        with open(dummy_file_path, 'w') as dummy_file:
            dummy_file.write(dummy_content)

        def request_callback(request):
            self.assertEqual(request.body.decode(), dummy_content)
            self.assertEqual(request.url, self.asset_url_params)
            self.assertEqual(request.headers['Content-Type'], 'text/markdown')
            self.assertEqual('token super-token', request.headers['Authorization'])

            return 201, {}, json.dumps({})

        responses.add_callback(
            responses.POST,
            self.asset_url,
            callback=request_callback
        )
        status = Github.upload_asset(
            'relekang', 'rmoq', 1, dummy_file_path, 'Dummy file')
        self.assertTrue(status)

        # Remove test file
        os.remove(dummy_file_path)

    @responses.activate
    @mock.patch('semantic_release.hvcs.Github.token', return_value='super-token')
    def test_should_upload_dists(self, mock_token):
        # Create temporary file to upload
        os.makedirs('/tmp/dist/', exist_ok=True)
        dummy_file_path = '/tmp/dist/testupload.md'
        dummy_content = '# Test File\n\n*Dummy asset for testing uploads.*'
        with open(dummy_file_path, 'w') as dummy_file:
            dummy_file.write(dummy_content)

        def request_callback(request):
            self.assertEqual(request.body.decode(), dummy_content)
            self.assertEqual(request.url, self.dist_asset_url_params)
            self.assertEqual(request.headers['Content-Type'], 'text/markdown')
            self.assertEqual('token super-token', request.headers['Authorization'])

            return 201, {}, json.dumps({})

        responses.add(
            responses.GET,
            self.get_url,
            status=200,
            body='{"id": 1}',
            content_type='application/json'
        )
        responses.add_callback(
            responses.POST,
            self.asset_url,
            callback=request_callback
        )
        status = Github.upload_dists('relekang', 'rmoq', '1.0.0', '/tmp/dist/')
        self.assertTrue(status)

        # Remove test file
        os.remove(dummy_file_path)


class GitlabReleaseTests(TestCase):

    @mock_gitlab()
    def test_should_return_true_if_success(self, mock_config, mock_auth, mock_project):
        self.assertTrue(post_changelog(
            'owner', 'repo', 'my_good_tag', 'changelog'
        ))

    @mock_gitlab()
    def test_should_return_false_if_bad_tag(self, mock_config, mock_auth, mock_project):
        self.assertFalse(post_changelog(
            'owner', 'repo', 'my_bad_tag', 'changelog'
        ))

    @mock_gitlab()
    def test_should_return_false_if_failed_update(self, mock_config, mock_auth, mock_project):
        self.assertFalse(post_changelog(
            'owner', 'repo', 'my_locked_tag', 'changelog'
        ))


def test_github_token():
    with mock.patch('os.environ', {'GH_TOKEN': 'token'}):
        assert(Github.token() == 'token')
