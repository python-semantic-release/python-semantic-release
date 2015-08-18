from unittest import TestCase

from semantic_release.errors import UnknownCommitMessageStyle
from semantic_release.history.parser_angular import parse_commit_message as angular_parser


class AngularCommitParserTests(TestCase):

    text = 'This is an long explanatory part of a commit message. It should give ' \
           'some insight to the fix this commit adds to the codebase.'
    footer = 'Closes #400'

    def test_parser_raises_unknown_message_style(self):
        self.assertRaises(UnknownCommitMessageStyle, angular_parser, '')

    def test_parser_return_correct_bump_level(self):
        self.assertEqual(
            angular_parser('feat(parsers): Add new parser pattern\n\nBREAKING CHANGE:')[0],
            3
        )
        self.assertEqual(
            angular_parser('feat(parsers): Add new parser pattern\n\n'
                           'New pattern is awesome\n\nBREAKING CHANGE:')[0],
            3
        )
        self.assertEqual(angular_parser('feat(parser): Add emoji parser')[0], 2)
        self.assertEqual(angular_parser('fix(parser): Fix regex in angular parser')[0], 1)
        self.assertEqual(angular_parser('test(parser): Add a test for angular parser')[0], 0)

    def test_parser_return_type_from_commit_message(self):
        self.assertEqual(angular_parser('feat(parser): ...')[1], 'feature')
        self.assertEqual(angular_parser('fix(parser): ...')[1], 'fix')
        self.assertEqual(angular_parser('test(parser): ...')[1], 'test')
        self.assertEqual(angular_parser('docs(parser): ...')[1], 'documentation')
        self.assertEqual(angular_parser('style(parser): ...')[1], 'style')
        self.assertEqual(angular_parser('refactor(parser): ...')[1], 'refactor')
        self.assertEqual(angular_parser('chore(parser): ...')[1], 'chore')

    def test_parser_return_scope_from_commit_message(self):
        self.assertEqual(angular_parser('chore(parser): ...')[2], 'parser')
        self.assertEqual(angular_parser('chore(a part): ...')[2], 'a part')
        self.assertEqual(angular_parser('chore(a_part): ...')[2], 'a_part')
        self.assertEqual(angular_parser('chore(a-part): ...')[2], 'a-part')

    def test_parser_return_subject_from_commit_message(self):
        self.assertEqual(
            angular_parser('feat(parser): Add emoji parser')[3][0],
            'Add emoji parser'
        )
        self.assertEqual(
            angular_parser('fix(parser): Fix regex in angular parser')[3][0],
            'Fix regex in angular parser'
        )
        self.assertEqual(
            angular_parser('test(parser): Add a test for angular parser')[3][0],
            'Add a test for angular parser'
        )

    def test_parser_return_text_from_commit_message(self):
        self.assertEqual(
            angular_parser('fix(parser): Fix regex in an parser\n\n{}'.format(self.text))[3][1],
            self.text
        )

    def test_parser_return_footer_from_commit_message(self):
        self.assertEqual(
            angular_parser('fix(tox): Fix env \n\n{t.text}\n\n{t.footer}'.format(t=self))[3][2],
            self.footer
        )
