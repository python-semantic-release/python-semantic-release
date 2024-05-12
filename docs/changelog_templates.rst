.. _changelog-templates:

Changelog Templates
===================

.. warning::
    If you have an existing changelog in the location you have configured with
    the :ref:`changelog_file <config-changelog-changelog_file>` setting,
    or if you have a template inside your :ref:`template directory <config-changelog-template_dir>`
    which will render to the location of an existing file, Python Semantic Release will
    overwrite the contents of this file.

    Please make sure to refer to :ref:`changelog-templates-migrating-existing-changelog`.

Python Semantic Release can write a changelog for your project. By default, it uses an
in-built template; once rendered this will be written to the location you configure with the
:ref:`changelog_file <config-changelog-changelog_file>` setting.

However, Python Semantic Release is also capable of rendering an entire directory tree
of templates during the changelog generation process. This directory is specified
using the :ref:`template directory <config-changelog-template_dir>` setting.

Python Semantic Release uses `Jinja`_ as its template engine, so you should refer to the
`Template Designer Documentation`_ for guidance on how to customize the appearance of
the files which are rendered during the release process. If you would like to customize
the template environment itself, then certain options are available to you via
:ref:`changelog environment configuration <config-changelog-environment>`.

Changelogs are rendered during the :ref:`cmd-version` and :ref:`cmd-changelog` commands.
You can disable changelog generation entirely during the :ref:`cmd-version` command by
providing the :ref:`--no-changelog <cmd-version-option-changelog>` command-line option.

The changelog template is re-rendered on each release.

.. _Jinja: https://jinja.palletsprojects.com/en/3.1.x/
.. _Template Designer Documentation: https://jinja.palletsprojects.com/en/3.1.x/templates/

.. _changelog-templates-template-rendering:

Template Rendering
------------------

.. _changelog-templates-template-rendering-directory-structure:

Directory Structure:
^^^^^^^^^^^^^^^^^^^^

If you don't want to set up your own custom changelog template, you can have Python
Semantic Release use its in-built template. If you would like to customize the
appearance of the changelog, or to render additional files, then you will need to
create a directory within your repository and set the :ref:`template_dir <config-changelog-template_dir>`
setting to the name of this directory. The default name is ``"templates"``.

.. note::
   It is *strongly* recommended that you use a dedicated top-level folder for the
   template directory.

When the templates are rendered, files within the tree are output to the location
within your repository that has the *same relative path* to the root as the *relative
path of the template to the templates directory*.

Templates are identified by giving a ``.j2`` extension to the template file. Any such
templates have the ``.j2`` extension removed from the target file. Therefore, to render
an output file ``foo.csv``, you should create a template called ``foo.csv.j2`` within
your template directory.

.. note::
   A file within your template directory which does *not* end in ``.j2`` will not
   be treated as a template; it will be copied to its target location without being
   rendered by the template engine.

Files within the template directory are *excluded* from the rendering process if the
file begins with a ``"."`` or if *any* of the folders containing this file begin with
a ``"."``.

.. _changelog-templates-template-rendering-directory-structure-example:

Directory Structure (Example)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose a project sets :ref:`template_dir <config-changelog-template_dir>` to
``"templates"`` and has the following structure:

.. code-block::

    example-project
    ├── src
    │   └── example_project
    │       └── __init__.py
    └── templates
        ├── CHANGELOG.md.j2
        ├── .components
        │   └── authors.md.j2
        ├── .macros.j2
        ├── src
        │   └── example_project
        │       └── data
        │           └── data.json.j2
        └── static
            └── config.cfg

After running a release with Python Semantic Release, the directory structure
of the project will now look like this:

.. code-block::

    example-project
    ├── CHANGELOG.md
    ├── src
    │   └── example_project
    │       ├── data
    │       │   └── data.json
    │       └── __init__.py
    ├── static
    │   └── config.cfg
    └── templates
        ├── CHANGELOG.md.j2
        ├── .components
        │   └── authors.md.j2
        ├── .macros.j2
        ├── src
        │   └── example_project
        │       └── data
        │           └── data.json.j2
        └── static
            └── config.cfg

Note that:

* There is no top-level ``.macros`` file created, because this file is excluded
  from the rendering process.
* There is no top-level ``.components`` directory created, because this folder and
  all files and folders contained within it are excluded from the rendering process.
* To render data files into the ``src/`` folder, the path to which the template should
  be rendered has to be created within the ``templates`` directory.
* The ``templates/static`` folder is created at the top-level of the project, and the
  file ``templates/static/config.cfg`` is *copied, not rendered* to the new top-level
  ``static`` folder.

You may wish to leverage this behaviour to modularise your changelog template, to
define macros in a separate file, or to reference static data which you would like
to avoid duplicating between your template environment and the remainder of your
project.

.. _changelog-templates-template-rendering-template-context:

Template Context
^^^^^^^^^^^^^^^^

Alongside the rendering of a directory tree, Python Semantic Release makes information
about the history of the project available within the templating environment in order
for it to be used to generate Changelogs and other such documents.

The history of the project is made available via the global variable ``context``. In
Python terms, ``context`` is a `dataclass`_ with the following attributes:

* ``repo_name: str``: the name of the current repository parsed from the Git url.
* ``repo_owner: str``: the owner of the current repository parsed from the Git url.
* ``hvcs_type: str``: the name of the VCS server type currently configured.
* ``history: ReleaseHistory``: a :py:class:`semantic_release.changelog.ReleaseHistory` instance.
  (See :ref:`changelog-templates-template-rendering-template-context-release-history`)
* ``filters: Tuple[Callable[..., Any], ...]``: a tuple of filters for the template environment.
  These are added to the environment's ``filters``, and therefore there should be no need to
  access these from the ``context`` object inside the template.

The filters provided vary based on the VCS configured and available features:

* ``create_server_url: Callable[[str, str | None, str | None, str | None], str]``: when given
  a path, prepend the configured vcs server host and url scheme.  Optionally you can provide,
  a auth string, a query string or a url fragment to be normalized into the resulting url.
  Parameter order is as described above respectively.

* ``create_repo_url: Callable[[str, str | None, str | None], str]``: when given a repository
  path, prepend the configured vcs server host, and repo namespace.  Optionally you can provide,
  an additional query string and/or a url fragment to also put in the url. Parameter order is
  as described above respectively. This is similar to ``create_server_url`` but includes the repo
  namespace and owner automatically.

* ``commit_hash_url: Callable[[str], str]``: given a commit hash, return a URL to the
  commit in the remote.

* ``compare_url: Callable[[str, str], str]``: given a starting git reference and a ending git
  reference create a comparison url between the two references that can be opened on the remote

* ``issue_url: Callable[[str | int], str]``: given an issue number, return a URL to the issue
  on the remote vcs.

* ``merge_request_url: Callable[[str | int], str]``: given a merge request number, return a URL
  to the merge request in the remote. This is an alias to the ``pull_request_url`` but only
  available for the VCS that uses the merge request terminology.

* ``pull_request_url: Callable[[str | int], str]``: given a pull request number, return a URL
  to the pull request in the remote. For remote vcs' that use merge request terminology, this
  filter is an alias to the ``merge_request_url`` filter function.

Availability of the documented filters can be found in the table below:

======================  =========  =====  ======  ======
**filter - hvcs_type**  bitbucket  gitea  github  gitlab
======================  =========  =====  ======  ======
create_server_url          ✅       ✅      ✅      ✅
create_repo_url            ✅       ✅      ✅      ✅
commit_hash_url            ✅       ✅      ✅      ✅
compare_url                ✅       ❌      ✅      ✅
issue_url                  ❌       ✅      ✅      ✅
merge_request_url          ❌       ❌      ❌      ✅
pull_request_url           ✅       ✅      ✅      ✅
======================  =========  =====  ======  ======

.. seealso::
   * `Filters <https://jinja.palletsprojects.com/en/3.1.x/templates/#filters>`_

.. _changelog-templates-template-rendering-template-context-release-history:

``ReleaseHistory``
""""""""""""""""""

A ``ReleaseHistory`` instance has two attributes: ``released`` and ``unreleased``.

The ``unreleased`` attribute is of type ``Dict[str, List[ParseResult]]``. Each commit
in the current branch's commit history since the last release on this branch is grouped
by the ``type`` attribute of the ``ParsedCommit`` returned by the commit parser,
or if the parser returned a ``ParseError`` then the result is grouped under the
``"unknown"`` key.

For this reason, every element of ``ReleaseHistory.unreleased["unknown"]`` is a
``ParseError``, and every element of every other value in ``ReleaseHistory.unreleased``
is of type ``ParsedCommit``.

Typically, commit types will be ``"feature"``, ``"fix"``, ``"breaking"``, though the
specific types are determined by the parser. For example, the
:py:class:`semantic_release.commit_parser.EmojiCommitParser` uses a textual
representation of the emoji corresponding to the most significant change introduced
in a commit (e.g. ``":boom:"``) as the different commit types. As a template author,
you are free to customise how these are presented in the rendered template.

.. note::
   If you are using a custom commit parser following the guide at
   :ref:`commit-parser-writing-your-own-parser`, your custom implementations of
   :py:class:`semantic_release.ParseResult`, :py:class:`semantic_release.ParseError`
   and :py:class:`semantic_release.ParsedCommit` will be used in place of the built-in
   types.

The ``released`` attribute is of type ``Dict[Version, Release]``. The keys of this
dictionary correspond to each version released within this branch's history, and
are of type ``semantic_release.Version``. You can use the ``as_tag()`` method to
render these as the Git tag that they correspond to inside your template.

A ``Release`` object has an ``elements`` attribute, which has the same
structure as the ``unreleased`` attribute of a ``ReleaseHistory``; that is,
``elements`` is of type ``Dict[str, List[ParseResult]]``, where every element
of ``elements["unknown"]`` is a ``ParseError``, and elements of every other
value correspond to the ``type`` attribute of the ``ParsedCommit`` returned
by the commit parser.

The commits represented within each ``ReleaseHistory.released[version].elements``
grouping are the commits which were made between ``version`` and the release
corresponding to the previous version.
That is, given two releases ``Version(1, 0, 0)`` and ``Version(1, 1, 0)``,
``ReleaseHistory.released[Version(1, 0, 0)].elements`` contains only commits
made after the release of ``Version(1, 0, 0)`` up to and including the release
of ``Version(1, 1, 0)``.

To maintain a consistent order of subsections in the changelog headed by the commit
type, it's recommended to use Jinja's `dictsort <https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.dictsort>`_
filter.

Each ``Release`` object also has the following attributes:

* ``tagger: git.Actor``: The tagger who tagged the release.
* ``committer: git.Actor``: The committer who made the release commit.
* ``tagged_date: datetime``: The date and time at which the release was tagged.

.. seealso::
   * :ref:`commit-parser-builtin`
   * :ref:`Commit Parser Tokens <commit-parser-tokens>`
   * `git.Actor <https://gitpython.readthedocs.io/en/stable/reference.html#git.objects.util.Actor>`_
   * `datetime.strftime Format Codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_

.. _dataclass: https://docs.python.org/3/library/dataclasses.html

.. _changelog-templates-customizing-vcs-release-notes:

Customizing VCS Release Notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same :ref:`template rendering <changelog-templates-template-rendering>` mechanism
generates the release notes when :ref:`creating VCS releases <index-creating-vcs-releases>`:

* the `in-built template`_ is used by default
* create a file named ``.release_notes.md.j2`` inside the project's
  :ref:`template_dir <config-changelog-template_dir>` to customize the release notes

.. _changelog-templates-customizing-vcs-release-notes-release-notes-context:

Release Notes Context
"""""""""""""""""""""

All of the changelog's
:ref:`template context <changelog-templates-template-rendering-template-context>` is
exposed to the `Jinja`_ template when rendering the release notes.

Additionally, the following two globals are available to the template:

* ``release`` (:class:`Release <semantic_release.changelog.release_history.Release>`):
  contains metadata about the content of the release, as parsed from commit logs
* ``version`` (:class:`Version <semantic_release.version.version.Version>`): contains
  metadata about the software version to be released and its ``git`` tag

.. _in-built template: https://github.com/python-semantic-release/python-semantic-release/blob/master/semantic_release/data/templates/release_notes.md.j2

.. _changelog-templates-release-notes-template-example:

Release Notes Template Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below is an example template that can be used to render release notes (it's similar to
GitHub's `automatically generated release notes`_):

.. code-block::

    ## What's Changed
    {% for type_, commits in release["elements"] | dictsort %}
    ### {{ type_ | capitalize }}
    {%- if type_ != "unknown" %}
    {% for commit in commits %}
    * {{ commit.descriptions[0] }} by {{commit.commit.author.name}} in [`{{ commit.short_hash }}`]({{ commit.hexsha | commit_hash_url }})
    {%- endfor %}{% endif %}{% endfor %}

.. _Automatically generated release notes: https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes

.. _changelog-templates-template-rendering-example:

Changelog Template Example
--------------------------

Below is an example template that can be used to render a Changelog:

.. code-block::

    # CHANGELOG
    {% if context.history.unreleased | length > 0 %}

    {# UNRELEASED #}
    ## Unreleased
    {% for type_, commits in context.history.unreleased | dictsort %}
    ### {{ type_ | capitalize }}
    {% for commit in commits %}{% if type_ != "unknown" %}
    * {{ commit.commit.message.rstrip() }} ([`{{ commit.commit.hexsha[:7] }}`]({{ commit.commit.hexsha | commit_hash_url }}))
    {% else %}
    * {{ commit.commit.message.rstrip() }} ([`{{ commit.commit.hexsha[:7] }}`]({{ commit.commit.hexsha | commit_hash_url }}))
    {% endif %}{% endfor %}{% endfor %}

    {% endif %}

    {# RELEASED #}
    {% for version, release in context.history.released.items() %}
    ## {{ version.as_tag() }} ({{ release.tagged_date.strftime("%Y-%m-%d") }})
    {% for type_, commits in release["elements"] | dictsort %}
    ### {{ type_ | capitalize }}
    {% for commit in commits %}{% if type_ != "unknown" %}
    * {{ commit.commit.message.rstrip() }} ([`{{ commit.commit.hexsha[:7] }}`]({{ commit.commit.hexsha | commit_hash_url }}))
    {% else %}
    * {{ commit.commit.message.rstrip() }} ([`{{ commit.commit.hexsha[:7] }}`]({{ commit.commit.hexsha | commit_hash_url }}))
    {% endif %}{% endfor %}{% endfor %}{% endfor %}

.. _changelog-templates-migrating-existing-changelog:

Migrating an Existing Changelog
-------------------------------

If you have an existing changelog that you would like to preserve, it's recommended
that you add the contents of this file to your changelog template - either directly
or via Jinja's `include <https://jinja.palletsprojects.com/en/3.1.x/templates/#include>`_
tag. If you would like only the history from your next release onwards to be rendered
into the changelog in addition to the existing changelog, you can add an `if statement
<https://jinja.palletsprojects.com/en/3.1.x/templates/#if>`_ based upon the versions in
the keys of ``context.released``.
