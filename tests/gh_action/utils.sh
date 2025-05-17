#!/bin/bash

# ------------------------------
# UTILS
# ------------------------------
IMAGE_TAG="${TEST_CONTAINER_TAG:?TEST_CONTAINER_TAG not set}"
PROJECT_MOUNT_DIR="${PROJECT_MOUNT_DIR:-"tmp/project"}"
GITHUB_ACTIONS_CWD="/github/workspace"

log() {
  printf '%b\n' "$*"
}

error() {
  log >&2 "\033[31m$*\033[0m"
}

explicit_run_cmd() {
  local cmd="$*"
  log "$> $cmd\n"
  eval "$cmd"
}

run_test() {
    local test_name="${1:?Test name not provided}"
    test_name="${test_name//_/ }"
    test_name="$(tr "[:lower:]" "[:upper:]" <<< "${test_name:0:1}")${test_name:1}"

    # Set Defaults based on action.yml
    [ -z "${WITH_VAR_DIRECTORY:-}" ] && local WITH_VAR_DIRECTORY="."
    [ -z "${WITH_VAR_CONFIG_FILE:-}" ] && local WITH_VAR_CONFIG_FILE=""
    [ -z "${WITH_VAR_NO_OPERATION_MODE:-}" ] && local WITH_VAR_NO_OPERATION_MODE="false"
    [ -z "${WITH_VAR_VERBOSITY:-}" ] && local WITH_VAR_VERBOSITY="1"

    # Extract all WITH_VAR_ variables dynamically from environment
    local ENV_ARGS=()
    args_in_env="$(compgen -A variable | grep "^WITH_VAR_")"
    read -r -a ENV_ARGS <<< "$(printf '%s' "$args_in_env" | tr '\n' ' ')"

    # Set Docker arguments (default: always remove the container after execution)
    local DOCKER_ARGS=("--rm")

    # Add all WITH_VAR_ variables to the Docker command
    local actions_input_var_name=""
    for input in "${ENV_ARGS[@]}"; do
        # Convert WITH_VAR_ to INPUT_ to simulate GitHub Actions input syntax
        actions_input_var_name="INPUT_${input#WITH_VAR_}"

        # Add the environment variable to the Docker command
        DOCKER_ARGS+=("-e ${actions_input_var_name}='${!input}'")
    done

    # Add the project directory to the Docker command
    DOCKER_ARGS+=("-v ${PROJECT_MOUNT_DIR}:${GITHUB_ACTIONS_CWD}")

    # Set the working directory to the project directory
    DOCKER_ARGS+=("-w ${GITHUB_ACTIONS_CWD}")

    # Run the test
    log "\n$test_name"
    log "--------------------------------------------------------------------------------"
    if ! explicit_run_cmd "docker run ${DOCKER_ARGS[*]} $IMAGE_TAG"; then
        return 1
    fi
}

export UTILS_LOADED="true"
