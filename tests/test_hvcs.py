import json
from unittest import TestCase

import responses

from semantic_release.errors import ImproperConfigurationError
from semantic_release.hvcs import Github, check_build_status, check_token, get_hvcs

from . import mock


class HCVSHelperTests(TestCase):
    def test_get_hvcs_should_return_github(self):
        self.assertEqual(get_hvcs(), Github)

    @mock.patch('semantic_release.hvcs.config.get', lambda *x: 'doesnotexist')
    def test_get_hvcs_should_raise_improper_config(self):
        self.assertRaises(ImproperConfigurationError, get_hvcs)

    @mock.patch('semantic_release.hvcs.Github.check_build_status')
    def test_check_build_status(self, mock_github_helper):
        check_build_status('owner', 'name', 'ref')
        mock_github_helper.assert_called_once_with('owner', 'name', 'ref')

    @mock.patch('semantic_release.hvcs.Github.token', lambda: 'token')
    def test_check_token_should_return_true(self):
        self.assertTrue(check_token())

    @mock.patch('semantic_release.hvcs.Github.token', lambda: None)
    def test_check_token_should_return_false(self):
        self.assertFalse(check_token())


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


class GithubReleaseTests(TestCase):
    url = 'https://api.github.com/repos/relekang/rmoq/releases'

    @responses.activate
    @mock.patch('semantic_release.hvcs.Github.token', lambda: 'super-token')
    def test_should_post_changelog(self):
        def request_callback(request):
            payload = json.loads(request.body)
            self.assertEqual(payload['tag_name'], 'v1.0.0')
            self.assertEqual(payload['body'], 'text')
            self.assertEqual(payload['draft'], False)
            self.assertEqual(payload['prerelease'], False)
            self.assertIn('?access_token=super-token', request.url)

            return 201, {}, json.dumps({})

        responses.add_callback(
            responses.POST,
            self.url,
            callback=request_callback,
            content_type='application/json'
        )
        status, payload = Github.post_release_changelog('relekang', 'rmoq', '1.0.0', 'text')
        self.assertTrue(status)
        self.assertEqual(payload, {})

    @responses.activate
    def test_should_return_false_status_if_it_failed(self):
        responses.add(
            responses.POST,
            self.url,
            status=400,
            body='{}',
            content_type='application/json'
        )
        self.assertFalse(Github.post_release_changelog('relekang', 'rmoq', '1.0.0', 'text')[0])
