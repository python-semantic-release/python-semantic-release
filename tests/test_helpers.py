from unittest import TestCase

import semantic_release
from semantic_release.helpers import get_current_version


class GetCurrentVersionTests(TestCase):

    def test_should_return_correct_version(self):
        self.assertEqual(get_current_version(), semantic_release.__version__)
