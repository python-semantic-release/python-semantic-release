.. _config-guides-uv_integration:

Ultraviolet (``uv``) Integration
================================

.. _uv: https://docs.astral.sh/uv/

`uv`_ is an extremely fast Python package and project manager that
provides a modern alternative to `pip <https://pip.pypa.io/en/stable/>`_
and `venv <https://docs.python.org/3/library/venv.html>`_. It provides a lot
of features that solve the common problems of Python package management but
it also introduces a few quirks that need to be taken into account when using
Python Semantic Release.

.. important::

  **Prerequisite:** Make sure you have run through the
  :ref:`Getting Started Guide <getting-started-guide>` before proceeding with
  this guide.


Updating the ``uv.lock``
------------------------

One of the best features of ``uv`` is that it automatically generates a lock file
(``uv.lock``) that contains the exact versions of all the dependencies used in
your project. The lock file is generated when you run the ``uv install`` command,
and it is used to ensure that CI workflows are repeatable and development environments
are consistent.

When creating a new release using Python Semantic Release, PSR will update the version
in the project's definition file (e.g., ``pyproject.toml``) to indicate the new version.
Unfortunately, this action will cause ``uv`` to fail on the next execution because the
lock file will be out of sync with the project's definition file. There are two ways to
resolve this issue depending on your preference:

#.  **Add a step to your build command**: Modify your
    :ref:`semantic_release.build_command <config-build_command>` to include the command
    to update the lock file and stage it for commit.  This is commonly used with the
    :ref:`GitHub Action <gh_actions-psr>` and other CI/CD tools when you are building
    the artifact at the time of release.

    .. code-block:: toml

      [tool.semantic_release]
      build_command = """
          uv lock --upgrade-package "$PACKAGE_NAME"
          git add uv.lock
          uv build
      """

    The intent of the lock upgrade-package call is **ONLY** to update
    the version of your project within the lock file after PSR has updated the version
    in your project's definition file (e.g., ``pyproject.toml``). When you are running
    PSR, you have already tested the project as is and you don't want to actually
    update the dependencies if a new one just became available.

    For ease of use, PSR provides the ``$PACKAGE_NAME`` environment variable that
    contains the name of your package from the project's definition file
    (``pyproject.toml:project.name``).

    If you are using the :ref:`PSR GitHub Action <gh_actions-psr>`, you will need to add an
    installation command for ``uv`` to the :ref:`build_command <config-build_command>`
    because the action runs in a Docker environment does not include ``uv`` by default.
    The best way to ensure that the correct version of ``uv`` is installed is to define
    the version of ``uv`` in an optional dependency list (e.g. ``build``). This will
    also help with other automated tools like Dependabot or Renovate to keep the version
    of ``uv`` up to date.

    .. code-block:: toml

      [project.optional-dependencies]
      build = ["uv ~= 0.7.12"]

      [tool.semantic_release]
      build_command = """
          python -m pip install -e '.[build]'
          uv lock --upgrade-package "$PACKAGE_NAME"
          git add uv.lock
          uv build
      """

#.  **Stamp the code first & then separately run release**: If you prefer to not modify the
    build command, then you will need to run the ``uv lock --upgrade-package <your-package-name>``
    command prior to actually creating the release. Essentially, you will run PSR twice:
    (1) once to update the version in the project's definition file, and (2) a second time
    to generate the release.

    The intent of the ``uv lock --upgrade-package <your-package-name>`` command is **ONLY**
    to update the version of your project within the lock file after PSR has updated the
    version in your project's definition file (e.g., ``pyproject.toml``). When you are
    running PSR, you have already tested the project as is and you don't want to actually
    update the dependencies if a new one just became available.

    .. code-block:: bash

      # 1. PSR stamps version into files (nothing else)
      # don't build the changelog (especially in update mode)
      semantic-release -v version --skip-build --no-commit --no-tag --no-changelog

      # 2. run UV lock as pyproject.toml is updated with the next version
      uv lock --upgrade-package <your-package-name>

      # 3. stage the lock file to ensure it is included in the PSR commit
      git add uv.lock

      # 4. run PSR fully to create release
      semantic-release -v version

**Advanced Example**

Of course, you can mix and match these 2 approaches as needed. If PSR's pipeline was using
``uv``, we would have a mixture of the 2 approaches because we run the build in a separate
job from the release. In our case, PSR would also need to carry the lock file as a workflow
artifact along the pipeline for the release job to commit it. This advanced workflow would
look like this:

.. code-block:: text

  # File: .tool-versions
  uv 0.7.12

.. code-block:: text

  # File: .python-version
  3.11.11

.. code-block:: toml

  # File: pyproject.toml
  [project.optional-dependencies]
  build = ["python-semantic-release ~= 10.0"]
  test = ["pytest ~= 8.0"]

  [tool.semantic_release]
  build_command = """
    uv lock --upgrade-package "$PACKAGE_NAME"
    uv build
  """

.. code-block:: yaml

  # File: .github/workflows/release.yml
  on:
    push:
      branches:
        - main

  jobs:

    build:
      runs-on: ubuntu-latest
      permissions:
        contents: read
      env:
        dist_artifacts_name: dist
        dist_artifacts_dir: dist
        lock_file_artifact: uv.lock
      steps:
        - name: Setup | Checkout Repository at workflow sha
          uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
          with:
            ref: ${{ github.sha }}

        - name: Setup | Force correct release branch on workflow sha
          run: git checkout -B ${{ github.ref_name }}

        - name: Setup | Install uv
          uses: asdf-vm/actions/install@1902764435ca0dd2f3388eea723a4f92a4eb8302  # v4.0.2

        - name: Setup | Install Python & Project dependencies
          run: uv sync --extra build

        - name: Build | Build next version artifacts
          id: version
          env:
            GH_TOKEN: "none"
          run: uv run semantic-release -v version --no-changelog --no-commit --no-tag

        - name: Upload | Distribution Artifacts
          if: ${{ steps.version.outputs.released == 'true' }}
          uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4.6.2
          with:
            name: ${{ env.dist_artifacts_name }}
            path: ${{ format('{0}/**', env.dist_artifacts_dir) }}
            if-no-files-found: error
            retention-days: 2

        - name: Upload | Lock File Artifact
          if: ${{ steps.version.outputs.released == 'true' }}
          uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4.6.2
          with:
            name: ${{ env.lock_file_artifact }}
            path: ${{ env.lock_file_artifact }}
            if-no-files-found: error
            retention-days: 2

      outputs:
        new-release-detected: ${{ steps.version.outputs.released }}
        new-release-version: ${{ steps.version.outputs.version }}
        new-release-tag: ${{ steps.version.outputs.tag }}
        new-release-is-prerelease: ${{ steps.version.outputs.is_prerelease }}
        distribution-artifacts: ${{ env.dist_artifacts_name }}
        lock-file-artifact: ${{ env.lock_file_artifact }}


    test-e2e:
      needs: build
      runs-on: ubuntu-latest
      steps:
        - name: Setup | Checkout Repository
          uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
          with:
            ref: ${{ github.sha }}
            fetch-depth: 1

        - name: Setup | Download Distribution Artifacts
          uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093  # v4.3.0
          if: ${{ needs.build.outputs.new-release-detected == 'true' }}
          id: artifact-download
          with:
            name: ${{ needs.build.outputs.distribution-artifacts }}
            path: ./dist

        - name: Setup | Install uv
          uses: asdf-vm/actions/install@1902764435ca0dd2f3388eea723a4f92a4eb8302  # v4.0.2

        - name: Setup | Install Python & Project dependencies
          run: uv sync --extra test

        - name: Setup | Install distribution artifact
          if: ${{ steps.artifact-download.outcome == 'success' }}
          run: |
            uv pip uninstall my-package
            uv pip install dist/python_semantic_release-*.whl

        - name: Test | Run pytest
          run: uv run pytest -vv tests/e2e


    release:
      runs-on: ubuntu-latest
      needs:
        - build
        - test-e2e

      if: ${{ needs.build.outputs.new-release-detected == 'true' }}

      concurrency:
        group: ${{ github.workflow }}-release-${{ github.ref_name }}
        cancel-in-progress: false

      permissions:
        contents: write

      steps:
        - name: Setup | Checkout Repository on Release Branch
          uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
          with:
            ref: ${{ github.ref_name }}

        - name: Setup | Force release branch to be at workflow sha
          run: git reset --hard ${{ github.sha }}

        - name: Setup | Install uv
          uses: asdf-vm/actions/install@1902764435ca0dd2f3388eea723a4f92a4eb8302  # v4.0.2

        - name: Setup | Install Python & Project dependencies
          run: uv sync --extra build

        - name: Setup | Download Build Artifacts
          uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093  # v4.3.0
          id: artifact-download
          with:
            name: ${{ needs.build.outputs.distribution-artifacts }}
            path: dist

        - name: Setup | Download Lock File Artifact
          uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093  # v4.3.0
          with:
            name: ${{ needs.build.outputs.lock-file-artifact }}

        - name: Setup | Stage Lock File for Version Commit
          run: git add uv.lock

        - name: Release | Create Release
          id: release
          shell: bash
          env:
            GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          run: |
            uv run semantic-release -v --strict version --skip-build
            uv run semantic-release publish

      outputs:
        released: ${{ steps.release.outputs.released }}
        new-release-version: ${{ steps.release.outputs.version }}
        new-release-tag: ${{ steps.release.outputs.tag }}


    deploy:
      name: Deploy
      runs-on: ubuntu-latest
      if: ${{ needs.release.outputs.released == 'true' && github.repository == 'python-semantic-release/my-package' }}
      needs:
        - build
        - release

      environment:
        name: pypi
        url: https://pypi.org/project/my-package/

      permissions:
        id-token: write

      steps:
        - name: Setup | Download Build Artifacts
          uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093  # v4.3.0
          id: artifact-download
          with:
            name: ${{ needs.build.outputs.distribution-artifacts }}
            path: dist

        - name: Publish package distributions to PyPI
          uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc  # v1.12.4
          with:
            packages-dir: dist
            print-hash: true
            verbose: true
