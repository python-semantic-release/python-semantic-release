#!/bin/bash

__file__="$(realpath "${BASH_SOURCE[0]}")"
__directory__="$(dirname "${__file__}")"

if ! [ "${UTILS_LOADED}" = "true" ]; then
    # shellcheck source=tests/utils.sh
    source "$__directory__/../utils.sh"
fi

# Common test constants
readonly TEST_GITHUB_TOKEN="ghp_1x2x3x4x5x6x7x8x9x0x1x2x3x4x5x6x7x8x9x0"
readonly TEST_SSH_PUBLIC_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITest"
readonly TEST_SSH_PRIVATE_KEY="-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----"
readonly TEST_GPG_PRIVATE_KEY="-----BEGIN PGP PRIVATE KEY BLOCK-----\ntest\n-----END PGP PRIVATE KEY BLOCK-----"

# Helper function to verify mutual exclusivity
# Parameters:
#   $1: test index
#   $2: test name
#   $3: ssh_public_key value (optional)
#   $4: ssh_private_key value (optional)
#   $5: description for error message
verify_mutual_exclusivity() {
    local index="${1:?Index not provided}"
    local test_name="${2:?Test name not provided}"
    local ssh_public="${3:-}"
    local ssh_private="${4:-}"
    local description="${5:?Description not provided}"

    # Set common env variables
    local WITH_VAR_GITHUB_TOKEN="$TEST_GITHUB_TOKEN"
    local WITH_VAR_NO_OPERATION_MODE="true"
    local WITH_VAR_VERBOSITY="1"
    local WITH_VAR_GPG_PRIVATE_SIGNING_KEY="$TEST_GPG_PRIVATE_KEY"
    
    # Set SSH keys if provided
    if [[ -n "$ssh_public" ]]; then
        local WITH_VAR_SSH_PUBLIC_SIGNING_KEY="$ssh_public"
    fi
    if [[ -n "$ssh_private" ]]; then
        local WITH_VAR_SSH_PRIVATE_SIGNING_KEY="$ssh_private"
    fi

    # Execute the test & capture output
    # This test should fail with a specific error message
    local output=""
    output="$(run_test "$index. $test_name" 2>&1)" && {
        # If the command succeeded, that's unexpected - the test should fail
        log "$output"
        error "Expected the action to fail when $description, but it succeeded!"
        error "::error:: $test_name failed!"
        return 1
    }

    # Evaluate the output to ensure the expected error message is present
    local expected_error="Both SSH and GPG signing keys are provided"
    if ! printf '%s' "$output" | grep -q "$expected_error"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find the expected error message in the output!"
        error "\tExpected Error: $expected_error"
        error "::error:: $test_name failed!"
        return 1
    fi

    log "\n$index. $test_name: PASSED!"
}

test_gpg_signing_error_when_both_ssh_and_gpg() {
    # Test that the action fails when both SSH and GPG signing keys are provided
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"
    
    verify_mutual_exclusivity "$index" "$test_name" \
        "$TEST_SSH_PUBLIC_KEY" \
        "$TEST_SSH_PRIVATE_KEY" \
        "both SSH keys and GPG key are provided"
}

test_gpg_signing_error_when_ssh_public_and_gpg() {
    # Test that the action fails when SSH public key and GPG signing key are provided
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"
    
    verify_mutual_exclusivity "$index" "$test_name" \
        "$TEST_SSH_PUBLIC_KEY" \
        "" \
        "SSH public key and GPG key are provided"
}

test_gpg_signing_error_when_ssh_private_and_gpg() {
    # Test that the action fails when SSH private key and GPG signing key are provided
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"
    
    verify_mutual_exclusivity "$index" "$test_name" \
        "" \
        "$TEST_SSH_PRIVATE_KEY" \
        "SSH private key and GPG key are provided"
}
