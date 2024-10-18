.. _commit-parsing:

Commit Parsing
==============

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

.. seealso::
  - :ref:`commit_parser <config-commit_parser>`
  - :ref:`commit_parser_options <config-commit_parser_options>`

.. _commit-parser-builtin:

Built-in Commit Parsers
-----------------------

The following parsers are built in to Python Semantic Release:

.. _commit-parser-angular:

``semantic_release.commit_parser.AngularCommitParser``
""""""""""""""""""""""""""""""""""""""""""""""""""""""

The default parser, which uses the `Angular commit style <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits>`_ with the following differences:

  - Multiple ``BREAKING CHANGE:`` paragraphs are supported
  - ``revert`` is not currently supported

The default configuration options for
:py:class:`semantic_release.commit_parser.AngularCommitParser` are:

.. code-block:: toml

    [tool.semantic_release.commit_parser_options]
    allowed_tags = [
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "style",
        "refactor",
        "test",
    ]
    minor_tags = ["feat"]
    patch_tags = ["fix", "perf"]

.. _commit-parser-emoji:

``semantic_release.history.EmojiCommitParser``
""""""""""""""""""""""""""""""""""""""""""""""

Parser for commits using one or more emojis as tags in the subject line.

If a commit contains multiple emojis, the one with the highest priority
(major, minor, patch, none) or the one listed first is used as the changelog
section for that commit. Commits containing no emojis go into an "Other"
section.

The default settings are for `Gitmoji <https://gitmoji.carloscuesta.me/>`_.

The default configuration options for
:py:class:`semantic_release.commit_parser.EmojiCommitParser` are:

.. code-block:: toml

    [tool.semantic_release.commit_parser_options]
    major_tags = [":boom:"]
    minor_tags = [
        ":sparkles:",
        ":children_crossing:",
        ":lipstick:",
        ":iphone:",
        ":egg:",
        ":chart_with_upwards_trend:",
    ]
    patch_tags = [
        ":ambulance:",
        ":lock:",
        ":bug:",
        ":zap:",
        ":goal_net:",
        ":alien:",
        ":wheelchair:",
        ":speech_balloon:",
        ":mag:",
        ":apple:",
        ":penguin:",
        ":checkered_flag:",
        ":robot:",
        ":green_apple:",
    ]

.. _commit-parser-scipy:

``semantic_release.history.scipy_parser``
"""""""""""""""""""""""""""""""""""""""""

A parser for `scipy-style commits <scipy-style>`_ with the following differences:

  - Beginning a paragraph inside the commit with ``BREAKING CHANGE`` declares
    a breaking change. Multiple ``BREAKING CHANGE`` paragraphs are supported.
  - A scope (following the tag in parentheses) is supported

The default configuration options for
:py:class:`semantic_release.commit_parser.ScipyCommitParser` are:

.. code-block:: toml

    [tool.semantic_release.commit_parser_options]
    allowed_tags = [
        "API",
        "DEP",
        "ENH",
        "REV",
        "BUG",
        "MAINT",
        "BENCH",
        "BLD",
        "DEV",
        "DOC",
        "STY",
        "TST",
        "REL",
        "FEAT",
        "TEST",
    ]
    major_tags = ["API"]
    minor_tags = ["DEP", "DEV", "ENH", "REV", "FEAT"]
    patch_tags = ["BLD", "BUG", "MAINT"]

.. _commit-parser-tag:

``semantic_release.history.TagCommitParser``
""""""""""""""""""""""""""""""""""""""""""""

.. warning::
  This parser was deprecated in ``v9.12.0``. It will be removed in a future release.

The original parser from v1.0.0 of Python Semantic Release. Similar to the
emoji parser above, but with less features.

The default configuration options for
:py:class:`semantic_release.commit_parser.TagCommitParser` are:

.. code-block:: toml

    [tool.semantic_release.commit_parser_options]
    minor_tag = ":sparkles:"
    patch_tag = ":nut_and_bolt:"

.. _commit-parser-writing-your-own-parser:

Writing your own parser
-----------------------

If you would prefer to use an alternative commit style, for example to adjust the
different ``type`` values that are associated with a particular commit, this is
possible.

The :ref:`commit_parser <config-commit_parser>` option, if set to a string which
does not match one of Python Semantic Release's inbuilt commit parsers, will be
used to attempt to dynamically import a custom commit parser class. As such you will
need to ensure that your custom commit parser is import-able from the environment in
which you are running Python Semantic Release. The string should be structured in the
standard ``module:attr`` format; for example, to import the class ``MyCommitParser``
from the file ``custom_parser.py`` at the root of your repository, you should specify
``"commit_parser=custom_parser:MyCommitParser"`` in your configuration, and run the
``semantic-release`` command line interface from the root of your repository. Equally
you can ensure that the module containing your parser class is installed in the same
virtual environment as semantic-release.
If you can run ``python -c "from $MODULE import $CLASS"`` successfully, specifying
``commit_parser="$MODULE:$CLASS"`` is sufficient. You may need to set the
``PYTHONPATH`` environment variable to the directory containing the module with
your commit parser.

Python Semantic Release provides several building blocks to help you write your parser.
To maintain compatibility with how Python Semantic Release will invoke your parser, you
should use the appropriate object as described below, or create your own object as a
subclass of the original which maintains the same interface. Type parameters are defined
where appropriate to assist with static type-checking.

.. _commit-parser-tokens:

Tokens
""""""
The tokens built into Python Semantic Release's commit parsing mechanism are inspired
by both the error-handling mechanism in `Rust's error handling`_ and its
implementation in `black`_. It is documented that `catching exceptions in Python is
slower`_ than the equivalent guard implemented using ``if/else`` checking when
exceptions are actually caught, so although ``try/except`` blocks are cheap if no
exception is raised, commit parsers should always return an object such as
:py:class:`semantic_release.ParseError` instead of raising an error immediately.
This is to avoid catching a potentially large number of parsing errors being caught
as the commit history of a repository is being parsed. Python Semantic Release does
not raise an exception if a commit cannot be parsed.

Python Semantic Release uses :py:class:`semantic_release.ParsedCommit`
as the return type of a successful parse operation, and :py:class:`semantic_release.ParseError`
as the return type from an unsuccessful parse of a commit. :py:class:`semantic_release.ParsedCommit` is a `namedtuple`_ which has the following fields:

* bump: a :py:class:`semantic_release.LevelBump` indicating what type of change this commit introduces.
* type: the *type* of the commit as a string, per the commit message style. This is up to the
  parser to implement; for example, the :py:class:`semantic_release.commit_parser.EmojiCommitParser`
  parser fills this field with the emoji representing the most significant change for the commit.
  The field is named after the representation in the Angular commit specification.
* scope: The scope, as a string, parsed from the commit. Commit styles which do not have a meaningful
  concept of "scope" should fill this field with an empty string.
* descriptions: A list of paragraphs (strings) (delimited by a double-newline) from the commit message.
* breaking_descriptions: A list of paragraphs (strings) which are deemed to identify and describe
  breaking changes by the parser. An example would be a paragraph which begins with the text
  ``BREAKING CHANGE:``.
* commit: The original commit object that was parsed.

:py:class:`semantic_release.ParseError` is a `namedtuple`_ which has the following fields:

* commit: The original commit object that was parsed.
* error: A string with a meaningful error message as to why the commit parsing failed.

In addition, :py:class:`semantic_release.ParseError` implements an additional method, ``raise_error``.
This method raises a :py:class:`semantic_release.CommitParseError` with the message contained in the
``error`` field, as a convenience.

:py:class:`ParsedCommit` and :py:class:`ParseError` objects also make the following
attributes available, each implemented as a ``property`` which is computed, as a
convenience for template authors - therefore custom implementations should ensure
these properties can also be computed:

* message: the ``message`` attribute of the ``commit``; where the message is of type ``bytes``
  this should be decoded to a ``UTF-8`` string.
* hexsha: the ``hexsha`` attribute of the ``commit``, representing its hash.
* short_hash: the first 7 characters of the ``hexsha`` attribute of the ``commit``.

In Python Semantic Release, the class :py:class:`semantic_release.ParseResult`
is defined as ``ParseResultType[ParsedCommit, ParseError]``, as a convenient shorthand.

:py:class:`semantic_release.ParseResultType` is a generic type, which
is the ``Union`` of its two type parameters. One of the types in this union should be the
type returned on a successful parse of the ``commit``, while the other should be the
type returned on an unsuccessful parse of the ``commit``.

A custom parser result type, therefore, could be implemented as follows:

* ``MyParsedCommit`` subclasses ``ParsedCommit``
* ``MyParseError`` subclasses ``ParseError``
* ``MyParseResult = ParseResultType[MyParsedCommit, MyParseError]``

Internally, Python Semantic Release uses ``isinstance`` to determine if the result
of parsing a commit was a success or not, so you should check that your custom result
and error types return ``True`` from ``isinstance(<object>, ParsedCommit)`` and
``isinstance(<object>, ParseError)`` respectively.

While it's not advisable to remove any of the fields that are available in the built-in
token types, currently only the ``bump`` field of the successful result type is used to
determine how the version should be incremented as part of this release. However, it's
perfectly possible to add additional fields to your tokens which can be populated by
your parser; these fields will then be available on each commit in your
:ref:`changelog template <changelog-templates>`, so you can make additional information
available.

.. _Rust's error handling: https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html
.. _black: https://github.com/psf/black/blob/main/src/black/rusty.py
.. _catching exceptions in Python is slower: https://docs.python.org/3/faq/design.html#how-fast-are-exceptions
.. _namedtuple: https://docs.python.org/3/library/typing.html#typing.NamedTuple

.. _commit-parsing-parser-options:

Parser Options
""""""""""""""

To provide options to the commit parser which is configured in the :ref:`configuration file
<configuration>`, Python Semantic Release includes a :py:class:`semantic_release.ParserOptions`
class. Each parser built into Python Semantic Release has a corresponding "options" class, which
subclasses :py:class:`semantic_release.ParserOptions`.

The configuration in :ref:`commit_parser_options <config-commit_parser_options>` is passed to the
"options" class which is specified by the configured :ref:`commit_parser <config-commit_parser>` -
more information on how this is specified is below.

The "options" class is used to validate the options which are configured in the repository,
and to provide default values for these options where appropriate.

If you are writing your own parser, you should accompany it with an "options" class
which accepts the appropriate keyword arguments. This class' ``__init__`` method should
store the values that are needed for parsing appropriately.

.. _commit-parsing-commit-parsers:

Commit Parsers
""""""""""""""

The commit parsers that are built into Python Semantic Release implement an instance
method called ``parse``, which takes a single parameter ``commit`` of type
`git.objects.commit.Commit <gitpython-commit-object>`_, and returns the type
:py:class:`semantic_release.ParseResultType`.

To be compatible with Python Semantic Release, a commit parser must subclass
:py:class:`semantic_release.CommitParser`. A subclass must implement
the following:

* A class-level attribute ``parser_options``, which must be set to
  :py:class:`semantic_release.ParserOptions` or a subclass of this.
* An ``__init__`` method which takes a single parameter, ``options``, that should be
  of the same type as the class' ``parser_options`` attribute.
* A method, ``parse``, which takes a single parameter ``commit`` that is of type
  `git.objects.commit.Commit <gitpython-commit-object>`_, and returns
  :py:class:`semantic_release.token.ParseResult`, or a subclass of this.

By default, the constructor for ``semantic_release.CommitParser`` will set the ``options``
parameter on the ``options`` attribute of the parser, so there is no need to override
this in order to access ``self.options`` during the ``parse`` method. However, if you
have any parsing logic that needs to be done only once, it may be a good idea to
perform this logic during parser instantiation rather than inside the ``parse`` method.
The parse method will be called once per commit in the repository's history during
parsing, so the effect of slow parsing logic within the ``parse`` method will be
magnified significantly for projects with sizeable Git histories.

Commit Parsers have two type parameters, "TokenType" and "OptionsType". The first
is the type which is returned by the ``parse`` method, and the second is the type
of the "options" class for this parser.

Therefore, a custom commit parser could be implemented via:

.. code-block:: python

    class MyParserOptions(semantic_release.ParserOptions):
        def __init__(self, message_prefix: str) -> None:
            self.prefix = message_prefix * 2


    class MyCommitParser(
        semantic_release.CommitParser[semantic_release.ParseResult, MyParserOptions]
    ):
        def parse(self, commit: git.objects.commit.Commit) -> semantic_release.ParseResult:
            ...

.. _angular commit guidelines: https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits
.. _gitpython-commit-object: https://gitpython.readthedocs.io/en/stable/reference.html#module-git.objects.commit
