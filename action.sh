#!/bin/bash

set -e

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"
export PYPI_TOKEN="${INPUT_PYPI_TOKEN}"
export REPOSITORY_USERNAME="${INPUT_REPOSITORY_USERNAME}"
export REPOSITORY_PASSWORD="${INPUT_REPOSITORY_PASSWORD}"
export PATH="${PATH}:/semantic-release/.venv/bin"

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
git config --global user.name "github-actions"
git config --global user.email "action@github.com"

# Run Semantic Release
/semantic-release/.venv/bin/python \
  -m semantic_release publish \
  -v DEBUG \
  -D commit_author="github-actions <action@github.com>" \
  "${INPUT_ADDITIONAL_OPTIONS}"
