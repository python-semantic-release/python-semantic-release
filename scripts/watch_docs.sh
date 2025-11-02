#!/bin/bash

if command -v realpath >/dev/null 2>&1; then
    PROJ_ROOT=$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")
elif command -v readlink >/dev/null 2>&1; then
    PROJ_ROOT=$(readlink -f "$(dirname "${BASH_SOURCE[0]}")/..")
else
    PROJ_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
fi

[ -z "$VIRTUAL_ENV" ] && VIRTUAL_ENV=".venv"
SPHINX_AUTOBUILD_EXE="$VIRTUAL_ENV/bin/sphinx-autobuild"

cd "$PROJ_ROOT" || exit 1

if [ ! -f "$SPHINX_AUTOBUILD_EXE" ]; then
    printf '%s\n' "sphinx-autobuild is not installed in the virtual environment. Please install the docs extras."
    exit 1
fi

rm -rf docs/_build/html docs/api/modules

exec "$SPHINX_AUTOBUILD_EXE" docs docs/_build/html --open-browser --port 9000 --ignore docs/api/modules
