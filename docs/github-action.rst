.. _github-action:

Python Semantic Release GitHub Action
=====================================

Python Semantic Release is also available as a GitHub action. Configuring the action
can be done in your workflow's YAML definition. The action provides the following
inputs:

Tokens
------
.. _action-github-token:

``github_token``
""""""""""""""""

The GitHub token used to push release notes and new commits/tags.

required: false

Artifact Repository
-------------------

.. _action-git-repository-username:

``repository_username``
"""""""""""""""""""""""

The username with project access to push to Artifact Repository

required: false

.. _action-git-repository-password:

``repository_password``
"""""""""""""""""""""""

The password or token to the account specified in repository_username

required: false

Custom Users
------------

.. _action-git-committer-name:

``git_committer_name``
""""""""""""""""""""""

The name of the account used to commit. If customized, it must be associated with the provided token. 

default: `github-actions`

required: false

.. _action-git-committer-email:

``git_committer_email``
""""""""""""""""""""""

The email of the account used to commit. If customized, it must be associated with the provided token. 

default: `actions@github.com>`

required: false

.. _action-ssh-public-signing-key:

``ssh_public_signing_key``
""""""""""""""""""""""

The public key used to verify a commit. If customized, it must be associated with the same account as the provided token. 

required: false

.. _action-ssh-private-signing-key:

``ssh_private_signing_key``
""""""""""""""""""""""

The private key used to verify a commit. If customized, it must be associated with the same account as the provided token. 

required: false

Additional Options
------------------

.. _action-directory:

``directory``
"""""""""""""

Sub-directory to cd into before running semantic-release

required: false

.. _action-additional-options:

``additional_options``
""""""""""""""""""""""

Additional options for the main ``semantic_release`` command. Example: ``-vv --noop``

required: false

default: ``-v``

.. _action-version-options:

``version_options``
"""""""""""""""""""

Additional options for the :ref:`cmd-version` command. Example: ``--patch``

required: false

.. _action-publish-options:

``publish_options``
"""""""""""""""""""

Additional options for the :ref:`cmd-publish` command. Example: ``--no-upload-to-repository``

required: false
