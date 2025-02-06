#!/bin/bash

set -e

# Convert "true"/"false" into command line args, returns "" if not defined
eval_boolean_action_input() {
	local -r input_name="$1"
	shift
	local -r flag_value="$1"
	shift
	local -r if_true="$1"
	shift
	local -r if_false="$1"

	if [ -z "$flag_value" ]; then
		echo ""
	elif [ "$flag_value" = "true" ]; then
		echo "$if_true"
	elif [ "$flag_value" = "false" ]; then
		echo "$if_false"
	else
		printf 'Error: Invalid value for input %s: %s is not "true" or "false\n"' \
			"$input_name" "$flag_value" >&2
		return 1
	fi
}

# Convert inputs to command line arguments
export ARGS=()
# v10 Breaking change as prerelease should be as_prerelease to match
ARGS+=("$(eval_boolean_action_input "prerelease" "$INPUT_PRERELEASE" "--as-prerelease" "")") || exit 1
ARGS+=("$(eval_boolean_action_input "commit" "$INPUT_COMMIT" "--commit" "--no-commit")") || exit 1
ARGS+=("$(eval_boolean_action_input "tag" "$INPUT_TAG" "--tag" "--no-tag")") || exit 1
ARGS+=("$(eval_boolean_action_input "push" "$INPUT_PUSH" "--push" "--no-push")") || exit 1
ARGS+=("$(eval_boolean_action_input "changelog" "$INPUT_CHANGELOG" "--changelog" "--no-changelog")") || exit 1
ARGS+=("$(eval_boolean_action_input "vcs_release" "$INPUT_VCS_RELEASE" "--vcs-release" "--no-vcs-release")") || exit 1
ARGS+=("$(eval_boolean_action_input "build" "$INPUT_BUILD" "" "--skip-build")") || exit 1
ARGS+=("$(eval_boolean_action_input "pep440" "$INPUT_PEP440" "--version-compat=pep440" "--version-compat=semver")") || exit 1

# Handle --patch, --minor, --major
# https://stackoverflow.com/a/47541882
valid_force_levels=("prerelease" "patch" "minor" "major")
if [ -z "$INPUT_FORCE" ]; then
	true # do nothing if 'force' input is not set
elif printf '%s\0' "${valid_force_levels[@]}" | grep -Fxzq "$INPUT_FORCE"; then
	ARGS+=("--$INPUT_FORCE")
else
	printf "Error: Input 'force' must be one of: %s\n" "${valid_force_levels[@]}" >&2
fi

if [ -n "$INPUT_BUILD_METADATA" ]; then
	ARGS+=("--build-metadata $INPUT_BUILD_METADATA")
fi

if [ -n "$INPUT_PRERELEASE_TOKEN" ]; then
	ARGS+=("--prerelease-token $INPUT_PRERELEASE_TOKEN")
fi

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
if ! [ "${INPUT_GIT_COMMITTER_NAME:="-"}" = "-" ]; then
	git config --global user.name "$INPUT_GIT_COMMITTER_NAME"
fi
if ! [ "${INPUT_GIT_COMMITTER_EMAIL:="-"}" = "-" ]; then
	git config --global user.email "$INPUT_GIT_COMMITTER_EMAIL"
fi
if [ "${INPUT_GIT_COMMITTER_NAME:="-"}" != "-" ] && [ "${INPUT_GIT_COMMITTER_EMAIL:="-"}" != "-" ]; then
	# Must export this value to the environment for PSR to consume the override
	export GIT_COMMIT_AUTHOR="$INPUT_GIT_COMMITTER_NAME <$INPUT_GIT_COMMITTER_EMAIL>"
fi

# See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124
# and https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956
git config --system --add safe.directory "*"

if [[ -n "$INPUT_SSH_PUBLIC_SIGNING_KEY" && -n "$INPUT_SSH_PRIVATE_SIGNING_KEY" ]]; then
	echo "SSH Key pair found, configuring signing..."

	# Write keys to disk
	mkdir -vp ~/.ssh
	echo -e "$INPUT_SSH_PUBLIC_SIGNING_KEY" >>~/.ssh/signing_key.pub
	cat ~/.ssh/signing_key.pub
	echo -e "$INPUT_SSH_PRIVATE_SIGNING_KEY" >>~/.ssh/signing_key
	# DO NOT CAT private key for security reasons
	sha256sum ~/.ssh/signing_key
	# Ensure read only private key
	chmod 400 ~/.ssh/signing_key

	# Enable ssh-agent & add signing key
	eval "$(ssh-agent -s)"
	ssh-add ~/.ssh/signing_key

	# Create allowed_signers file for git
	if [ "${INPUT_GIT_COMMITTER_EMAIL:="-"}" = "-" ]; then
		echo >&2 "git_committer_email must be set to use SSH key signing!"
		exit 1
	fi
	touch ~/.ssh/allowed_signers
	echo "$INPUT_GIT_COMMITTER_EMAIL $INPUT_SSH_PUBLIC_SIGNING_KEY" >~/.ssh/allowed_signers

	# Configure git for signing
	git config --global gpg.format ssh
	git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
	git config --global user.signingKey ~/.ssh/signing_key
	git config --global commit.gpgsign true
	git config --global tag.gpgsign true
fi

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"

# Run Semantic Release (explicitly use the GitHub action version)
eval "/psr/.venv/bin/semantic-release $INPUT_ROOT_OPTIONS version ${ARGS[*]}"
