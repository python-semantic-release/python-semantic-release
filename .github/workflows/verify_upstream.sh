#!/bin/bash

set -eu +o pipefail

# Example output of `git status -sb`:
#   ## master...origin/master [behind 1]
#   M .github/workflows/verify_upstream.sh
UPSTREAM_BRANCH_NAME="$(git status -sb | head -n 1 | cut -d' ' -f2 | grep -E '\.{3}' | cut -d'.' -f4)"
printf '%s\n' "Upstream branch name: $UPSTREAM_BRANCH_NAME"

set -o pipefail

if [ -z "$UPSTREAM_BRANCH_NAME" ]; then
    printf >&2 '%s\n' "::error::Unable to determine upstream branch name!"
    exit 1
fi

git fetch "${UPSTREAM_BRANCH_NAME%%/*}"

if ! UPSTREAM_SHA="$(git rev-parse "$UPSTREAM_BRANCH_NAME")"; then
    printf >&2 '%s\n' "::error::Unable to determine upstream branch sha!"
    exit 1
fi

HEAD_SHA="$(git rev-parse HEAD)"

if [ "$HEAD_SHA" != "$UPSTREAM_SHA" ]; then
    printf >&2 '%s\n' "[HEAD SHA] $HEAD_SHA != $UPSTREAM_SHA [UPSTREAM SHA]"
    printf >&2 '%s\n' "::error::Upstream has changed, aborting release..."
    exit 1
fi

printf '%s\n' "Verified upstream branch has not changed, continuing with release..."
