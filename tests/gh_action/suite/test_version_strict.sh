#!/bin/bash

__file__="$(realpath "${BASH_SOURCE[0]}")"
__directory__="$(dirname "${__file__}")"

if ! [ "${UTILS_LOADED:-false}" = "true" ]; then
    # shellcheck source=tests/utils.sh
    source "$__directory__/../utils.sh"
fi

test_version_strict() {
    # Using default configuration within PSR with no modifications
    # triggering the NOOP mode to prevent errors since the repo doesn't exist
    # We are just trying to test that the root options & tag arguments are
    # passed to the action without a fatal error
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"

    # Create expectations & set env variables that will be passed in for Docker command
    local WITH_VAR_GITHUB_TOKEN="ghp_1x2x3x4x5x6x7x8x9x0x1x2x3x4x5x6x7x8x9x0"
    local WITH_VAR_NO_OPERATION_MODE="true"
    local WITH_VAR_STRICT="true"
    local expected_psr_cmd=".*/bin/semantic-release -v --strict --noop version"
    # Since the example project is at the latest release, we expect strict mode
    # to fail with a non-zero exit code

    # Execute the test & capture output
    local output=""
    if output="$(run_test "$index. $test_name" 2>&1)"; then
        # Log the output for debugging purposes
        log "$output"
        error "Strict mode should of exited with a non-zero exit code but didn't!"
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