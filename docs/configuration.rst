.. _configuration:

Configuration
-------------

All configuration options described here can be overloaded in a ``setup.cfg``
file in a ``semantic_release`` section and/or in a ``pyproject.toml`` file in
a ``[tool.semantic_release]`` section. ``pyproject.toml`` is loaded after
``setup.cfg`` and has the priority.

Moreover, those configuration values can be overloaded with the ``-D`` option, like so ::

    semantic-release <command> -D <option_name>=<option_value>

``version_variable``
    The filename and variable name of where the
    version number is stored, e.g. ``semantic_release/__init__.py:__version__``.

``version_source``
    The way we get and set the new version. Can be ``commit`` or ``tag``.
    If set to ``tag``, will get the current version from the latest tag matching ``vX.Y.Z``.
    This won't change the source defined in ``version_variable``.
    If set to ``commit`` (default), will get the current version from the source defined
    in ``version_variable``, edit the file and commit it.

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

``hvcs``
    The name of your hvcs. Currently only ``github`` and ``gitlab`` are supported.
    Default: ``github``

``commit_version_number``
    Whether or not to commit changes when bumping version.
    Default: True if ``version_source`` is `tag`, False if ``version_source`` is `commit`.
