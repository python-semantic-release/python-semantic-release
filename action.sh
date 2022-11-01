#!/bin/bash

set -e

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"
export PYPI_TOKEN="${INPUT_PYPI_TOKEN}"
export REPOSITORY_USERNAME="${INPUT_REPOSITORY_USERNAME}"
export REPOSITORY_PASSWORD="${INPUT_REPOSITORY_PASSWORD}"
export PATH="${PATH}:/semantic-release/.venv/bin"
export GIT_COMMITER_NAME="${INPUT_GIT_COMMITER_NAME:="github-actions"}"
export GIT_COMMITER_EMAIL="${INPUT_GIT_COMMITER_EMAIL:="github-actions@github.com"}"

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
git config --global user.name "$GIT_COMMITER_NAME"
git config --global user.email "$GIT_COMMITER_EMAIL"

# Run Semantic Release
/semantic-release/.venv/bin/python \
  -m semantic_release publish \
  -v DEBUG \
  -D commit_author="$GIT_COMMITER_NAME <$GIT_COMMITER_EMAIL>" \
  ${INPUT_ADDITIONAL_OPTIONS}
