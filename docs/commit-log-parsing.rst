.. _commit-log-parsing:

Parsing of commit logs
**********************

The semver level that should be bumped on a release is determined by the
commit messages since the last release. In order to be able to decide the correct
version and generate the changelog, the content of those commit messages must
be parsed. By default this package uses a parser for the Angular commit message
style::

    <type>(<scope>): <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <footer>

The body or footer can begin with ``BREAKING CHANGE:`` followed by a short
description to create a major release.

.. note::
  Python Semantic Release is able to parse more than just the body and footer
  sections (in fact, they are processed in a loop so you can write as many
  paragraphs as you need). It also supports having multiple breaking changes
  in one commit.

  However, other tools may not do this, so if you plan to use any similar
  programs then you should try to stick to the official format.

More information about the style can be found in the `angular commit guidelines`_.

Available parsers
=================

See :ref:`config-commit_parser`.

Writing your own parser
=======================
If you think this is all well and cool, but the angular style is not for you,
no need to worry because custom parsers are supported.

A parser is basically a Python function that takes the commit message as the
only argument and returns the information extracted from the commit. The format
of the output should be a :py:class:`semantic_release.history.parser_helpers.ParsedCommit`
object with the following parameters::

    ParsedCommit(
      level to bump: major=3 minor=2 patch=1 none=0,
      type of change,
      scope of change: can be None,
      (subject, descriptions...),
      (breaking change descriptions...)
    )

The breaking change descriptions will be added to the changelog in full. They
can and should also be included within the regular list of description
paragraphs. The presence of a breaking change description will *not* implicitly
trigger a major release.

If your parser is unable to parse a commit then it should raise
:py:class:`semantic_release.UnknownCommitMessageStyleError`.

The parser can be set with the :ref:`config-commit_parser` configuration option.

.. _angular commit guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
