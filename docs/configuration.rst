.. _configuration:

Configuration
-------------

All configuration described here belongs in ``setup.cfg`` in a section:
``semantic_release``.

``version_variable``
    The filename and variable name of where the
    version number is stored, e.g. ``semantic_release/__init__.py:__version__``.

``commit_parser``
    Import path to a python function that can parse commit messages and return
    information about the commit as described in :ref:`commit-log-parsing`.

``patch_without_tag``
    If set to true semantic-release will create a new release
    even if there is no tag in any commits since last release. Default: false.

``check_build_status``
    If set to true the status of the head commit will be
    checked and a release will only be created if the status is success. Default: false.

``upload_to_pypi``
    If set to false the pypi uploading will be disabled. This can be useful to create
    tag releases for non-pypi projects.

``commit_message``
    Long description to append to the version number. This can be useful to skip
    pipelines in your CI tool

``dist_path``
    The relative path to the folder for dists configured for setuptools. This allows for
    customized setuptools processes. Default dist.

``remove_dist``
    Flag for whether the dist folder should be removed after a release. Default: true

``branch``
    The branch to run releases from. Default: master
