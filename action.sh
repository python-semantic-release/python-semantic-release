#!/bin/bash

set -el

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"
export PYPI_TOKEN="${INPUT_PYPI_TOKEN}"
export PYPI_USERNAME="${INPUT_PYPI_USERNAME}"
export PYPI_PASSWORD="${INPUT_PYPI_PASSWORD}"
export PATH="${PATH}:/semantic-release/.venv/bin"

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
git config --global user.name "github-actions"
git config --global user.email "action@github.com"

# Run Semantic Release
/semantic-release/.venv/bin/python -m semantic_release publish -v DEBUG \
  -D commit_author="github-actions <action@github.com>"
