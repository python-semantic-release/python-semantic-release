.. _algorithm:

Python Semantic Release's Version Bumping Algorithm
===================================================

Below is a technical description of the algorithm which Python Semantic Release
uses to calculate a new version for a project.

.. _algorithm-assumptions:

Assumptions
~~~~~~~~~~~

* At runtime, we are in a Git repository with HEAD referring to a commit on
  some branch of the repository (i.e. not in detached HEAD state).
* We know in advance whether we want to produce a prerelease or not (based on
  the configuration and command-line flags).
* We can parse the tags of the repository into semantic versions, as we are given
  the format that those Git tags should follow via configuration, but cannot
  cherry-pick only tags that apply to commits on specific branches. We must parse
  all tags in order to ensure we have parsed any that might apply to commits in
  this branch's history.
* If we can identify a commit as a ``merge-base`` between our HEAD commit and one
  or more tags, then that merge-base should be unique.
* We know ahead of time what ``prerelease_token`` to use for prereleases - e.g.
  ``rc``.
* We know ahead of time whether ``major`` changes introduced by commits
  should cause the new version to remain on ``0.y.z`` if the project is already
  on a ``0.`` version - see :ref:`major_on_zero <config-major_on_zero>`.

.. _algorithm-implementation:

Implementation
~~~~~~~~~~~~~~

1. Parse all the Git tags of the repository into semantic versions, and **sort**
   in descending (most recent first) order according to `semver precedence`_.
   Ignore any tags which do not correspond to valid semantic vesrions according
   to ``tag_format``.


2. Find the ``merge-base`` of HEAD and the latest tag according to the sort above.
   Call this commit ``M``.
   If there are no tags in the repo's history, we set ``M=HEAD``.

3. Find the latest non-prerelease version whose tag references a commit that is
   an ancestor of ``M``. We do this via a breadth-first search through the commit
   lineage, starting against ``M``, and for each tag checking if the tag
   corresponds to that commit. We break from the search when we find such a tag.
   If no such tag is found, see 4a).
   Else, suppose that tag corresponds to a commit ``L`` - goto 4b).

4.
    a. If no commit corresponding to the last non-prerelease version is found,
       the entire history of the repository is considered. We parse every commit
       that is an ancestor of HEAD to determine the type of change introduced -
       either ``major``, ``minor``, ``patch``, ``prerelease_revision`` or
       ``no_release``. We store this levels in a ``set`` as we only require
       the distinct types of change that were introduced.
    b. However, if we found a commit ``L`` which is the commit against which the
       last non-prerelease was tagged, then we parse only the commits from HEAD
       as far back as ``L``, to understand what changes have been introduced
       since the previous non-prerelease. We store these levels - either
       ``major``, ``minor``, ``patch``, ``prerelease_revision``, or
       ``no_release``, in a set, as we only require the distinct types of change
       that were introduced.

    c. We look for tags that correspond to each commit during this process, to
       identify the latest pre-release that was made within HEAD's ancestry.

5. If there have been no changes since the last non-prerelease, or all commits
   since that release result in a ``no_release`` type according to the commit
   parser, then we **terminate the algorithm.**

6. If we have not exited by this point, we know the following information:

  * The latest version, by `semver precedence`_, within the whole repository.
    Call this ``LV``. This might not be within the ancestry of HEAD.
  * The latest version, prerelease or non-prerelease, within the whole repository.
    Call this ``LVH``. This might not be within the ancestry of HEAD.
    This may be the same as ``LV``.
  * The latest non-prerelease version within the ancestry of HEAD. Call this
    ``LVHF``. This may be the same as ``LVH``.
  * The most significant type of change introduced by the commits since the
    previous full release. Call this ``level``
  * Whether or not we wish to produce a prerelease from this version increment.
    Call this a boolean flag, ``prerelease``. (Assumption)
  * Whether or not to increment the major digit if a major change is introduced
    against an existing ``0.`` version. Call this ``major_on_zero``, a boolean
    flag. (Assumption)

  Using this information, the new version is decided according to the following
  criteria:

  a. If ``LV`` has a major digit of ``0``, ``major_on_zero`` is ``False`` and
     ``level`` is ``major``, reduce ``level`` to ``minor``.

  b. If ``prerelease=True``, then

     i. Diff ``LV`` with ``LVHF``, to understand if the ``major``, ``minor`` or
        ``patch`` digits have changed. For example, diffing ``1.2.1`` and
        ``1.2.0`` is a ``patch`` diff, while diffing ``2.1.1`` and ``1.17.2`` is
        a ``major`` diff. Call this ``DIFF``

     ii. If ``DIFF`` is less semantically significant than ``level``, for example
         if ``DIFF=patch`` and ``level=minor``, then

         1. Increment the digit of ``LVF`` corresponding to ``level``, for example
            the minor digit if ``level=minor``, setting all less significant
            digits to zero.

         2. Add ``prerelease_token`` as a suffix result of 1., together with a
            prerelease revision number of ``1``. Return this new version and
            **terminate the algorithm.**

         Thus if ``DIFF=patch``, ``level=minor``, ``prerelease=True``,
         ``prerelease_token="rc"``, and ``LVF=1.1.1``,
         then the version returned by the algorithm is ``1.2.0-rc.1``.

     iii. If ``DIFF`` is semantically less significant than or equally
          significant to ``level``, then this means that the significance
          of change introduced by ``level`` is already reflected in a
          prerelease version that has been created since the last full release.
          For example, if ``LVHF=1.1.1``, ``LV=1.2.0-rc.1`` and ``level=minor``.

          In this case we:

          1. If the prerelease token of ``LV`` is different from
             ``prerelease_token``, take the major, minor and patch digits
             of ``LV`` and construct a prerelease version using our given
             ``prerelease_token`` and a prerelease revision of ``1``. We
             then return this version and **terminate the algorithm.**

             For example, if ``LV=1.2.0-rc.1`` and ``prerelease_token=alpha``,
             we return ``1.2.0-alpha.1``.

          2. If the prerelease token of ``LV`` is the same as ``prerelease_token``,
             we increment the revision number of ``LV``, return this version, and

             **terminate the algorithm.**
             For example, if ``LV=1.2.0-rc.1`` and ``prerelease_token=rc``,
             we return ``1.2.0-rc.2``.

  c. If ``prerelease=False``, then

    i. If ``LV`` is not a prerelease, then we increment the digit of ``LV``
       corresponding to ``level``, for example the minor digit if ``level=minor``,
       setting all less significant digits to zero.
       We return the result of this and **terminate the algorithm**.

    ii. If ``LV`` is a prerelease, then:

      1. Diff ``LV`` with ``LVHF``, to understand if the ``major``, ``minor`` or
         ``patch`` digits have changed. Call this ``DIFF``

      2. If ``DIFF`` is less semantically significant than ``level``, then

        i. Increment the digit of ``LV`` corresponding to ``level``, for example
           the minor digit if ``level=minor``, setting all less significant
           digits to zero.

        ii. Remove the prerelease token and revision number from the result of i.,
            ("Finalize" the result of i.) return the result and **terminate the
            algorithm.**

            For example, if ``LV=1.2.2-alpha.1`` and ``level=minor``, we return
            ``1.3.0``.

      3. If ``DIFF`` is semantically less significant than or equally
         significant to ``level``, then we finalize ``LV``, return the
         result and **terminate the algorithm**.

.. _semver precedence: https://semver.org/#spec-item-11

.. _algorithm-complexity:

Complexity
~~~~~~~~~~

**Space:**

A list of parsed tags takes ``O(number of tags)`` in space. Parsing each commit during
the breadth-first search between ``merge-base`` and the latest tag in the ancestry
of HEAD takes at worst ``O(number of commits)`` in space to track visited commits.
Therefore worst-case space complexity will be linear in the number of commits in the
repo, unless the number of tags significantly exceeds the number of commits
(in which case it will be linear in the number of tags).

**Time:**

Assuming using regular expression parsing of each tag is a constant-time operation,
then the following steps contribute to the time complexity of the algorithm:

* Parsing each tag - ``O(number of tags)``
* Sorting tags by `semver precedence`_ -
  ``O(number of tags * log(number of tags))``
* Finding the merge-base of HEAD and the latest release tag -
  ``O(number of commits)`` (worst case)
* Parsing each commit and checking each tag against each commit -
  ``O(number of commits) + O(number of tags * number of commits)``
  (worst case)

Overall, assuming that the number of tags is less than or equal to the number
of commits in the repository, this would lead to a worst-case time complexity
that's quadratic in the number of commits in the repo.
