.. _multibranch-releases:

Multibranch Releases
====================

Python Semantic Release supports releases from multiple branches within your Git
repository. You can elect to have a branch or set of branches create releases or
`prereleases`_. There are no restrictions enforced on how you set up your
releases, but be aware that if you create new releases from multiple branches,
or prereleases from multiple independent branches using the same
*prerelease token*, there is a chance that Python Semantic Release will calculate
the next version to be the same on more than one branch
(leading to an error that a Git tag already exists).

.. note::
    A "prerelease token" is the string used to suffix onto the 3-digit form of a full
    semantic version. For example, in the version ``1.2.3-beta.1``, the prerelease token
    is ``"beta"``

    Typical strings used for pre-release tokens include "alpha", "beta", "dev" and "rc".
    These tend to indicate a level of maturity of the software associated with the
    version, but the specific meaning of each string is up to the project to decide.

    Generally, it's good practice to maintain a single branch from which full releases
    are made, and one branch at a time for each type of prerelease (alpha, beta, rc, etc).

If you absolutely require tagging and (pre-)releases to take place from multiple branches
where there's a risk that tags could conflict between branches, you can use the
:ref:`--build-metadata <cmd-version-option-build-metadata>` command line argument to
attach additional information (such as the branch name) to the tag in order to uniquely
distinguish it from any other tags that might be calculated against other branches. Such
a situation may occur in the following scenario:

.. code-block::

                   O ----------- O      <---- feature-1
                  /          "feat: abc"
                 /
     O -------- O --------------- O    <---- main
  v1.0.0     v1.1.0
                  \
                   O ----------- O    <---- feature-2
                             "feat: 123"

Suppose that Python Semantic Release has been configured to use the same
prerelease token ``"alpha"`` for all ``feature-*`` branches, and the default tag
format ``"v{version}"``. In this case, running a pre-release from branch ``feature-1``
will recognize that since the last release, ``1.1.0``, a **feature** has been
introduced and therefore the next tag to be applied to ``feature-1`` will be
``v1.2.0-alpha.1``.

However, suppose we then try to run a release against ``feature-2``. This will also
recognize that a **feature** has been introduced against the last released version of
``v1.1.0`` and therefore will try to create the tag ``v1.2.0-alpha.1``, leading to an
error as this tag was already created against ``feature-1``.

To get around this issue, you can pass the branch name as part of the build metadata:

.. code-block:: shell

   semantic-release version --build-metadata $(git branch --show-current)

This would lead to the tag ``v1.2.0-alpha.1+feature-1`` and ``v1.2.0-alpha.1+feature-2``
being applied to branches ``feature-1`` and ``feature-2``, respectively. Note that
"`build metadata MUST be ignored`_" per the semver specification when comparing two
versions, so these two prereleases would be considered equivalent semantic versions,
but when merged to the branch configured to produce full releases (``main``), if
released separately the changes from each branch would be released in two versions
that would be considered different according to the semver specification.

.. note::

   If you have tags in your Git repository that are not valid semantic versions
   (which have then been formatted into your :ref:`tag_format <config-tag_format>`),
   these tags will be ignored for the purposes of calculating the next version.

.. _prereleases: https://semver.org/#spec-item-9
.. _build metadata MUST be ignored: https://semver.org/#spec-item-10

.. _multibranch-releases-configuring:

Configuring Multibranch Releases
--------------------------------

Within your configuration file, you can create one or more groups of branches
(*"release groups"*) that produce a certain type of release. Options are configured
at the group level, and the group to use is chosen based on the *current branch name*
against which Python Semantic Release is running.

Each release group is configured as a nested mapping under the
``tool.semantic_release.branches`` key in ``pyproject.toml``, or the equivalent
structure in other formats. the mapping requires a single key that is used as a
name for the release group, which can help to identify it in log messages but has
no effect on the behavior of the release. For example, Python Semantic Release has
only one release group by default with the name ``main``.

Inside each release group, the following key-value pairs can be set:

+----------------------+----------+-----------+--------------------------------------------------------+
| Key                  | Required | Default   | Description                                            |
+----------------------+----------+-----------+--------------------------------------------------------+
| match                | Yes      | N/A       | A `Python regular expression`_ to match against the    |
|                      |          |           | active branch's name. If the branch name matches the   |
|                      |          |           | provided regular expression, then this release group   |
|                      |          |           | is chosen to provide the other configuration settings  |
|                      |          |           | available.                                             |
+----------------------+----------+-----------+--------------------------------------------------------+
| prerelease           | No       | ``false`` | Whether or not branches in this release group should   |
|                      |          |           | a prerelease instead of a full release                 |
+----------------------+----------+-----------+--------------------------------------------------------+
| prerelease_token     | No       | ``rc``    | If creating a prerelease, specify the string to be     |
|                      |          |           | used as a prerelease token in any new versions created |
|                      |          |           | against this branch.                                   |
+----------------------+----------+-----------+--------------------------------------------------------+

.. _Python regular expression: https://docs.python.org/3/library/re.html

.. warning::
   If two release groups have overlapping "match" patterns, i.e. a the name of a branch could
   theoretically match both patterns, then the release group which is defined first in your
   configuration file is used.

   Because of this, it's recommended that you place release groups
   with more specific match patterns higher up in your configuration file than those with patterns
   that would match a broader range of branch names.

For example, suppose a project currently on version ``1.22.4`` is working on a new major version. The
project wants to create a branch called ``2.x.x`` against which they will develop the new major version,
and they would like to create "release candidate" ("rc") prereleases from this branch.
There are also a number of new features to integrate, and the project has agreed that all such branches
should be named according to the convention ``next-{developer initials}-{issue number}``, leading to
branches named similarly to ``next-bc-prj-123``. The project would like to release with tags that include
some way to identify the branch and date on which the release was made from the tag.

This project would be able to leverage the following configuration to achieve the above requirements
from their release configuration:

.. code-block:: toml

   [tool.semantic_release.branches.main]
   match = "(main|master)"
   prerelease = false

   [tool.semantic_release.branches."2.x.x"]
   match = "2.x.x"
   prerelease = true
   prerelease_token = "rc"

   [tool.semantic_release.branches."2.x.x New Features"]
   match = "next-\\w+-prj-\\d+"
   prerelease = true
   prerelease_token = "alpha"

In a CI pipeline, the following command would allow attaching the date and branch name
to the versions that are produced (note this example uses the UNIX ``date`` command):

.. code-block:: bash

   semantic-release version \
      --build-metadata "$(git branch --show-current).$(date +%Y%m%d)"

This would lead to versions such as ``1.1.1+main.20221127`` or ``2.0.0-rc.4+2.x.x.20221201``.

.. note::
   Remember that is always possible to override the release rules configured by using
   the :ref:`cmd-version-option-force-level` and :ref:`cmd-version-option-as-prerelease`
   flags.
