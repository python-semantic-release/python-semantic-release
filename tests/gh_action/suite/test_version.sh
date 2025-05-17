#!/bin/bash

__file__="$(realpath "${BASH_SOURCE[0]}")"
__directory__="$(dirname "${__file__}")"

if ! [ "${UTILS_LOADED}" = "true" ]; then
    # shellcheck source=tests/utils.sh
    source "$__directory__/../utils.sh"
fi

test_version() {
    # Using default configuration within PSR with no modifications
    # triggering the NOOP mode to prevent errors since the repo doesn't exist
    # We are just trying to test that the root options & tag arguments are
    # passed to the action without a fatal error
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"

    # Create expectations & set env variables that will be passed in for Docker command
    local WITH_VAR_GITHUB_TOKEN="ghp_1x2x3x4x5x6x7x8x9x0x1x2x3x4x5x6x7x8x9x0"
    local WITH_VAR_NO_OPERATION_MODE="true"
    local WITH_VAR_VERBOSITY="2"
    local expected_psr_cmd=".*/bin/semantic-release -vv --noop version"

    # Execute the test & capture output
    # Fatal errors if exit code is not 0
    local output=""
    if ! output="$(run_test "$index. $test_name" 2>&1)"; then
        # Log the output for debugging purposes
        log "$output"
        error "fatal error occurred!"
        error "::error:: $test_name failed!"
        return 1
    fi

    # Evaluate the output to ensure the expected command is present
    if ! printf '%s' "$output" | grep -q -E "$expected_psr_cmd"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find the expected command in the output!"
        error "\tExpected Command: $expected_psr_cmd"
        error "::error:: $test_name failed!"
        return 1
    fi

    log "\n$index. $test_name: PASSED!"
}

test_version_w_custom_config() {
    # Using default configuration within PSR with no modifications
    # triggering the NOOP mode to prevent errors since the repo doesn't exist
    # We are just trying to test that the root options & tag arguments are
    # passed to the action without a fatal error
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"

    # Create expectations & set env variables that will be passed in for Docker command
    local WITH_VAR_GITHUB_TOKEN="ghp_1x2x3x4x5x6x7x8x9x0x1x2x3x4x5x6x7x8x9x0"
    local WITH_VAR_NO_OPERATION_MODE="true"
    local WITH_VAR_VERBOSITY="0"
    local WITH_VAR_CONFIG_FILE="releaserc.toml"
    local expected_psr_cmd=".*/bin/semantic-release --config $WITH_VAR_CONFIG_FILE --noop version"

    # Execute the test & capture output
    # Fatal errors if exit code is not 0
    local output=""
    if ! output="$(run_test "$index. $test_name" 2>&1)"; then
        # Log the output for debugging purposes
        log "$output"
        error "fatal error occurred!"
        error "::error:: $test_name failed!"
        return 1
    fi

    # Evaluate the output to ensure the expected command is present
    if ! printf '%s' "$output" | grep -q "$expected_psr_cmd"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find the expected command in the output!"
        error "\tExpected Command: $expected_psr_cmd"
        error "::error:: $test_name failed!"
        return 1
    fi

    log "\n$index. $test_name: PASSED!"
}
