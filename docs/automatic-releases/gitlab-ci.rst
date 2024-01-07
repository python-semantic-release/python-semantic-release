.. _github-actions:

Setting up python-semantic-release on Gitlab CI
====================================================

Python Semantic Release can run on Gitlab CI using two mechanisms.
The first one uses a personal access token and the second one uses a Job Token.

Gitlab Ci `Job Token <https://docs.gitlab.com/ee/ci/jobs/ci_job_token.html>`_ are generated on the fly when a CI
pipeline is triggered.
The token has the same permissions to access the API as the user that caused the job to run, but with a subset of API
routes available. While safer than a
`Personal Access Token (PAT) <https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html>`_, it is not able
to push new commits to the repository although discussions are ongoing on the subject (cfr `issue 389060
<https://gitlab.com/gitlab-org/gitlab/-/issues/389060>`_).


Using a personal access token (PAT)
-------------------------------------

Once you have `created a PAT <https://docs.gitlab.com/ee/user/profile/personal_access_tokens
.html#create-a-personal-access-token>`_,  you can add it as a secret variable in your Gitlab CI project under the
name GL_TOKEN.

In order to use gitlab token you need to configure python semantic release by adding the following to your
pyproject.toml file:

.. code:: toml

    [tool.semantic_release]
    remote.type = "gitlab"

Normally using  the following .gitlab-ci.yml should be enough to get you started:

.. code:: yaml

    stages:
      - publish # Deploy new version of package to registry

    # Official language image. Look for the different tagged releases at:
    # https://hub.docker.com/r/library/python/tags/
    image: python:latest

    variables:
      PIP_CACHE_DIR: $CI_PROJECT_DIR/.cache/pip # Set folder in working dir for cache

    # Runs on commit in main branch that were not made by the semantic-release job
    version_and_publish:
      stage: publish
      image: python:latest
      variables:
        GIT_DEPTH: 0
      before_script:
        - pip install python-semantic-release
        - pip install twine
      script:
        - git checkout "$CI_COMMIT_REF_NAME"
        - semantic-release version
        - |
          if [ "dist" ]; then
            TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token python -m twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*
          fi
      cache:
        paths:
          - ${PIP_CACHE_DIR}
      rules:
        # Don't run on automatic commits
        - if: $CI_COMMIT_AUTHOR =~ /semantic-release.*/
          when: never
        # Only run on main/master branch
        - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

Using a Job Token
------------------
In order to use gitlab-ci job token you need to configure python semantic release by adding the following to your
pyproject.toml file:

.. code:: toml

    [tool.semantic_release]
    remote.type = "gitlab-ci"
    remote.ignore_token_for_push = "true"

The following workflow is proposed to the reader.

A `Project Access Token <https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html>`_ is created in Gitlab and given the right to push to the main branch.
This token is added as a secret variable in your Gitlab CI project under the name ``GL_PROJECT_TOKEN_NAME`` and
``GL_PROJECT_TOKEN``. This token should only have write access to the repository, it does not require API access.
If you are using Gitlab Premium or Ultimate, you can make this token a guest to further restrain the token's scope,
and specify it as the sole person allowed to push to the master branch.
Otherwise, you will have to grant that project access token a sufficiently high access privilege that it can push to
the main branch.

The following .gitlab-ci.yml should be enough to get you started:

.. code:: yaml

    stages:
      - publish # Deploy new version of package to registry

    # Official language image. Look for the different tagged releases at:
    # https://hub.docker.com/r/library/python/tags/
    image: python:latest

    variables:
      PIP_CACHE_DIR: $CI_PROJECT_DIR/.cache/pip # Set folder in working dir for cache

    # Runs on commit in main branch that were not made by the semantic-release job
    # Using GITLAB_USER_EMAIL in the GIT_COMMIT_AUTHOR will display the person who
    # triggered the job either by clicking the merge button or pushing to master
    # as the author of the commit.
    version_and_publish:
      stage: publish
      image: python:latest
      variables:
        GIT_DEPTH: 0
        GIT_COMMIT_AUTHOR: "$GL_PROJECT_TOKEN_NAME <$GITLAB_USER_EMAIL>"
      before_script:
        - pip install python-semantic-release
        - pip install twine
      script:
        - git checkout "$CI_COMMIT_REF_NAME"
        - git remote set-url origin https://${GL_PROJECT_TOKEN_NAME}:${GL_PROJECT_TOKEN}@${CI_REPOSITORY_URL#*@}
        - semantic-release version
        - |
          if [ "dist" ]; then
            TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token python -m twine upload --repository-url ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi dist/*
          fi
      cache:
        paths:
          - ${PIP_CACHE_DIR}
      rules:
        # Don't run on automatic commits
        - if: $CI_COMMIT_AUTHOR =~ /$GL_PROJECT_TOKEN_NAME.*/
          when: never
        # Only run on main/master branch
        - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
