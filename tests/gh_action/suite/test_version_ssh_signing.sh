#!/bin/bash

__file__="$(realpath "${BASH_SOURCE[0]}")"
__directory__="$(dirname "${__file__}")"

if ! [ "${UTILS_LOADED}" = "true" ]; then
    # shellcheck source=tests/utils.sh
    source "$__directory__/../utils.sh"
fi

test_version_ssh_signing() {
    # Test that SSH signing keys are correctly configured in the action
    # We will generate an SSH key pair and pass it to the action to ensure
    # the ssh-agent and ssh-add commands work correctly
    local index="${1:?Index not provided}"
    local test_name="${FUNCNAME[0]}"

    # Generate a temporary SSH key pair for testing
    local ssh_key_dir
    ssh_key_dir="$(mktemp -d)"
    local ssh_private_key_file="$ssh_key_dir/signing_key"
    local ssh_public_key_file="$ssh_key_dir/signing_key.pub"

    # Generate SSH key pair (Ed25519 for faster generation and smaller keys)
    # Note: Using empty passphrase (-N "") for test purposes only
    if ! ssh-keygen -t ed25519 -N "" -f "$ssh_private_key_file" -C "test@example.com" >/dev/null 2>&1; then
        error "Failed to generate SSH key pair!"
        rm -rf "$ssh_key_dir"
        return 1
    fi

    # Read the generated keys
    local ssh_public_key
    local ssh_private_key
    ssh_public_key="$(cat "$ssh_public_key_file")"
    ssh_private_key="$(cat "$ssh_private_key_file")"

    # Clean up the temporary key files
    rm -rf "$ssh_key_dir"

    # Create expectations & set env variables that will be passed in for Docker command
    local WITH_VAR_GITHUB_TOKEN="ghp_1x2x3x4x5x6x7x8x9x0x1x2x3x4x5x6x7x8x9x0"
    local WITH_VAR_NO_OPERATION_MODE="true"
    local WITH_VAR_VERBOSITY="2"
    local WITH_VAR_GIT_COMMITTER_NAME="Test User"
    local WITH_VAR_GIT_COMMITTER_EMAIL="test@example.com"
    local WITH_VAR_SSH_PUBLIC_SIGNING_KEY="$ssh_public_key"
    local WITH_VAR_SSH_PRIVATE_SIGNING_KEY="$ssh_private_key"

    # Expected messages in output
    local expected_ssh_setup_msg="SSH Key pair found, configuring signing..."
    local expected_psr_cmd=".*/bin/semantic-release -vv --noop version"

    # Execute the test & capture output
    local output=""
    if ! output="$(run_test "$index. $test_name" 2>&1)"; then
        # Log the output for debugging purposes
        log "$output"
        error "fatal error occurred!"
        error "::error:: $test_name failed!"
        return 1
    fi

    # Evaluate the output to ensure SSH setup message is present
    if ! printf '%s' "$output" | grep -q "$expected_ssh_setup_msg"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find SSH setup message in the output!"
        error "\tExpected Message: $expected_ssh_setup_msg"
        error "::error:: $test_name failed!"
        return 1
    fi

    # Evaluate the output to ensure ssh-agent was started successfully
    if ! printf '%s' "$output" | grep -q "Agent pid"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find ssh-agent start message in the output!"
        error "\tExpected Message pattern: 'Agent pid'"
        error "::error:: $test_name failed!"
        return 1
    fi

    # Evaluate the output to ensure ssh-add was successful
    if ! printf '%s' "$output" | grep -q "Identity added"; then
        # Log the output for debugging purposes
        log "$output"
        error "Failed to find ssh-add success message in the output!"
        error "\tExpected Message pattern: 'Identity added'"
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
