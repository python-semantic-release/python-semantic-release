#!/bin/bash

function load_base_env() {
    set -eu -o pipefail

    local __FILE__=""
    __FILE__="$(realpath "${BASH_SOURCE[0]}")"

    PROJ_ROOT_DIR="$(realpath "$(dirname "$(realpath "$(dirname "$__FILE__")")")")"
    export PROJ_ROOT_DIR

    export DIST_DIR="$PROJ_ROOT_DIR/dist"
    export SCRIPTS_DIR="$PROJ_ROOT_DIR/scripts"
    export VENV_DIR="$PROJ_ROOT_DIR/.venv"
    export PROJECT_CONFIG_FILE="$PROJ_ROOT_DIR/pyproject.toml"
    export MINIMUM_PYTHON_VERSION="3.9"
    export PIP_DISABLE_PIP_VERSION_CHECK="true"
}

function stdout { printf "%b\n" "$*"; }
function stderr { stdout "$@" >&2; }
function info { stdout "[+] $*"; }

function warning {
    local prefix="[!] "
    if [ "${CI:-false}" = "true" ] && [ -n "${GITHUB_ACTIONS:-}" ]; then
        prefix="::notice::"
    fi
    stderr "${prefix}WARNING: $*";
}

function error {
    local prefix="[-] "
    if [ "${CI:-false}" = "true" ] && [ -n "${GITHUB_ACTIONS:-}" ]; then
        prefix="::error::"
    fi
    stderr "${prefix}ERROR: $*";
}

function is_command {
    local cmd="${1:?"param[1]: missing command to check."}"
    command -v "$cmd" >/dev/null || {
        error "Command '$cmd' not found."
        return 1
    }
}

function explicit_run_cmd {
    local cmd="${1:?"param[1]: command not specified, but is required!"}"
    set -- "${@:2}" # shift off the first argument
    local args="$*"

    # Default as a function call
    local log_msg="$cmd($args)"

    # Needs to run in bash because zsh which will return 0 for a defined function
    if bash -c "which $cmd >/dev/null"; then
        log_msg="${SHELL:-/bin/sh} -c '$cmd $args'"
    fi

    stderr "    $log_msg"
    eval "$cmd $args"
}

function explicit_run_cmd_w_status_wrapper {
    local status_msg="${1:?"param[1]: status message not specified, but is required!"}"
    local cmd="${2:?"param[2]: command not specified, but is required!"}"
    set -- "${@:3}" # shift off the first two arguments

    if [ -z "$cmd" ]; then
        error "Command not specified, but is required!"
        return 1
    fi

    info "${status_msg}..."
    if ! explicit_run_cmd "$cmd" "$@"; then
        error "${status_msg}...FAILED"
        return 1
    fi
    info "${status_msg}...DONE"
}

function verify_python_version() {
    local python3_exe="${1:?"param[1]: path to python3 executable is required"}"
    local min_version="${2:?"param[2]: minimum python version is required"}"

    if ! [[ "$min_version" =~ ^v?[0-9]+(\.[0-9]+){0,2}$ ]]; then
        error "Invalid minimum python version format: '$min_version'. Expected format: 'X', 'X.Y', or 'X.Y.Z'"
        return 1
    fi

    local min_major_version=""
    min_major_version="$(stdout "$min_version" | cut -d. -f1 | tr -d 'v')"

    local min_minor_version=""
    min_minor_version="$(stdout "$min_version" | cut -d. -f2)"
    min_minor_version="${min_minor_version:-0}"

    local min_patch_version=""
    min_patch_version="$(stdout "$min_version" | cut -d. -f3)"
    min_patch_version="${min_patch_version:-0}"

    local python_version_str=""
    if ! python_version_str="$("$python3_exe" --version 2>&1 | awk '{print $2}')"; then
        error "Failed to get python version string from '$python3_exe'"
        return 1
    fi

    local python_major_version=""
    python_major_version="$(stdout "$python_version_str" | cut -d. -f1)"

    local python_minor_version=""
    python_minor_version="$(stdout "$python_version_str" | cut -d. -f2)"

    local python_patch_version=""
    python_patch_version="$(stdout "$python_version_str" | cut -d. -f3)"

    if [ "$python_major_version" -ne "$min_major_version" ]; then
        error "Python major version mismatch! Required version: $min_major_version, Found version: $python_version_str"
        return 1
    fi

    if [ "$python_minor_version" -lt "$min_minor_version" ] || [ "$python_patch_version" -lt "$min_patch_version" ]; then
        error "Python version ^${min_major_version}.${min_minor_version}.${min_patch_version}+ is required! Found version: $python_version_str"
        return 1
    fi
}

function verify_python() {
    set -eu -o pipefail
    local -r min_python_version="${1:?"param[1]: minimum python version parameter is required!"}"

    is_command "python3" || {
        error "Python 3 is not detected. Script requires Python $min_python_version+!"
        return 1
    }

    local python3_exe=""
    python3_exe="$(which python3)"

    if ! [ -f "$(dirname "$python3_exe")/../pyvenv.cfg" ]; then
        error "No virtual environment detected."
        return 1
    fi

    verify_python_version "$python3_exe" "$min_python_version"
}

export UTILITIES_SH_LOADED="true"
