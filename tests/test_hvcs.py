import json
from unittest import TestCase, mock

import responses

from semantic_release.errors import ImproperConfigurationError
from semantic_release.hvcs import Github, check_build_status, get_hvcs


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
