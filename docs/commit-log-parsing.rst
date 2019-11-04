.. _commit-log-parsing:

Parsing of commit logs
----------------------

The semver level that should be bumped on a release is determined by the
commit messages since last release. In order to be able to decide the correct
version and generate the changelog the content of those commit messages must
be parsed. By default this package uses a parser for the Angular commit message
style(:py:func:`semantic_release.history.parser_angular.parse_commit_message`).
The commit message style is as follows::

    <type>(<scope>): <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <footer>

More information about the Angular commit message style can be found in the
`angular commit guidelines`_.

Writing your own parser
~~~~~~~~~~~~~~~~~~~~~~~
If you think this is all well and cool, but the angular style is not for you.
No need to worry because custom parsers are supported. A parser is basically
a python function that takes the commit message as the only argument and
returns a tuple with the information needed to evaluate the commit and build
the changelog. The format of the output should be as follows::

    (level to bump, type of change, scope of change, (subject, body, footer))

The type of change can be one of `feature`, `fix` or any string in lowercase.
The `feature` will result in an minor release and `fix` or `perf` indicates a patch release.
To create a major release the body in the last item in the tuple must contain::

    BREAKING CHANGE: <explanation>

If your parser does not recognise the commit style or in other words is unable
to parse it then it should raise :py:class:`semantic_release.UnknownCommitMessageStyleError`.

The parser can be set with the ``commit_parser`` configuration option. See :ref:`configuration`.

.. _angular commit guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
