#!/bin/bash

set -e

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"
export PYPI_TOKEN="${INPUT_PYPI_TOKEN}"
export REPOSITORY_USERNAME="${INPUT_REPOSITORY_USERNAME}"
export REPOSITORY_PASSWORD="${INPUT_REPOSITORY_PASSWORD}"
export PATH="${PATH}:/semantic-release/.venv/bin"
export GIT_COMMITTER_NAME="${INPUT_GIT_COMMITTER_NAME:="github-actions"}"
export GIT_COMMITTER_EMAIL="${INPUT_GIT_COMMITTER_EMAIL:="github-actions@github.com"}"
export SSH_PRIVATE_SIGNING_KEY="${INPUT_SSH_PRIVATE_SIGNING_KEY}"
export SSH_PUBLIC_SIGNING_KEY="${INPUT_SSH_PUBLIC_SIGNING_KEY}"

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
git config --global user.name "$GIT_COMMITTER_NAME"
git config --global user.email "$GIT_COMMITTER_EMAIL"

# See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124
# and https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956
git config --system --add safe.directory "*"

if [[  -n $SSH_PUBLIC_SIGNING_KEY && -n $SSH_PRIVATE_SIGNING_KEY ]]; then
    echo "SSH Key pair found, configuring signing..."
    mkdir ~/.ssh
    echo -e "$SSH_PRIVATE_SIGNING_KEY" >> ~/.ssh/signing_key
    cat ~/.ssh/signing_key
    echo -e "$SSH_PUBLIC_SIGNING_KEY" >> ~/.ssh/signing_key.pub
    cat ~/.ssh/signing_key.pub
    chmod 600 ~/.ssh/signing_key && chmod 600 ~/.ssh/signing_key.pub
    eval "$(ssh-agent)"
    ssh-add ~/.ssh/signing_key
    git config --global gpg.format ssh
    git config --global user.signingKey ~/.ssh/signing_key
    git config --global commit.gpgsign true
    git config --global user.email $GIT_COMMITTER_EMAIL
    git config --global user.name $GIT_COMMITTER_NAME
    touch ~/.ssh/allowed_signers
    echo "$GIT_COMMITTER_EMAIL $SSH_PUBLIC_SIGNING_KEY" > ~/.ssh/allowed_signers
    git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
fi

# Run Semantic Release
/semantic-release/.venv/bin/python \
  -m semantic_release publish \
  -v DEBUG \
  -D commit_author="$GIT_COMMITTER_NAME <$GIT_COMMITTER_EMAIL>" \
  ${INPUT_ADDITIONAL_OPTIONS}
