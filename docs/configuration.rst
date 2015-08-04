Configuration
-------------

All configuration described here belongs in ``setup.cfg`` in a section:
``semantic-release``.

``version_variable``
    The filename and variable name of where the
    version number is stored, e.g. ``semantic_release/__init__.py:__version__``.

``patch_without_tag``
    If set to true semantic-release will create a new release
    even if there is no tag in any commits since last release. Default: false.

``check_build_status``
    If set to true the status of the head commit will be
    checked and a release will only be created if the status is success. Default: false.

Commit message evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~

There are a set of tags used to evaluate the changes from commit
messages. They can be configured to meet what you want them to be. The
different tags are listed below with their defaults.

-  **Major change:** ``major_tag = :boom:``
-  **Minor change:** ``minor_tag = :sparkles:``
-  **Patch change:** ``patch_tag = :bug:``
