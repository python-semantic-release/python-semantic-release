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

# Copy inputs into correctly-named environment variables
export GH_TOKEN="${INPUT_GITHUB_TOKEN}"
export PATH="${PATH}:/semantic-release/.venv/bin"
export GIT_COMMITTER_NAME="${INPUT_GIT_COMMITTER_NAME:="github-actions"}"
export GIT_COMMITTER_EMAIL="${INPUT_GIT_COMMITTER_EMAIL:="github-actions@github.com"}"
export SSH_PRIVATE_SIGNING_KEY="${INPUT_SSH_PRIVATE_SIGNING_KEY}"
export SSH_PUBLIC_SIGNING_KEY="${INPUT_SSH_PUBLIC_SIGNING_KEY}"
export GIT_COMMIT_AUTHOR="${GIT_COMMITTER_NAME} <${GIT_COMMITTER_EMAIL}>"
export ROOT_OPTIONS="${INPUT_ROOT_OPTIONS:="-v"}"
# v10 BREAKING CHANGE, to correct this input value to match cli?
export PRERELEASE="${INPUT_PRERELEASE:="false"}"
export COMMIT="${INPUT_COMMIT:="false"}"
export PUSH="${INPUT_PUSH:="false"}"
export CHANGELOG="${INPUT_CHANGELOG:="false"}"
export VCS_RELEASE="${INPUT_VCS_RELEASE:="false"}"

# Convert inputs to command line arguments
export ARGS=()
# v10 Breaking change?
ARGS+=("$(eval_boolean_action_input "prerelease" "$PRERELEASE" "--as-prerelease" "")") || exit 1
ARGS+=("$(eval_boolean_action_input "commit" "$COMMIT" "--commit" "--no-commit")") || exit 1
ARGS+=("$(eval_boolean_action_input "tag" "$INPUT_TAG" "--tag" "--no-tag")") || exit 1
ARGS+=("$(eval_boolean_action_input "push" "$PUSH" "--push" "--no-push")") || exit 1
ARGS+=("$(eval_boolean_action_input "changelog" "$CHANGELOG" "--changelog" "--no-changelog")") || exit 1
ARGS+=("$(eval_boolean_action_input "vcs_release" "$VCS_RELEASE" "--vcs-release" "--no-vcs-release")") || exit 1

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

# Change to configured directory
cd "${INPUT_DIRECTORY}"

# Set Git details
git config --global user.name "$GIT_COMMITTER_NAME"
git config --global user.email "$GIT_COMMITTER_EMAIL"

# See https://github.com/actions/runner-images/issues/6775#issuecomment-1409268124
# and https://github.com/actions/runner-images/issues/6775#issuecomment-1410270956
git config --system --add safe.directory "*"

if [[ -n "$SSH_PUBLIC_SIGNING_KEY" && -n "$SSH_PRIVATE_SIGNING_KEY" ]]; then
	echo "SSH Key pair found, configuring signing..."
	mkdir ~/.ssh
	echo -e "$SSH_PRIVATE_SIGNING_KEY" >>~/.ssh/signing_key
	cat ~/.ssh/signing_key
	echo -e "$SSH_PUBLIC_SIGNING_KEY" >>~/.ssh/signing_key.pub
	cat ~/.ssh/signing_key.pub
	chmod 600 ~/.ssh/signing_key && chmod 600 ~/.ssh/signing_key.pub
	eval "$(ssh-agent)"
	ssh-add ~/.ssh/signing_key
	git config --global gpg.format ssh
	git config --global user.signingKey ~/.ssh/signing_key
	git config --global commit.gpgsign true
	git config --global user.email "$GIT_COMMITTER_EMAIL"
	git config --global user.name "$GIT_COMMITTER_NAME"
	touch ~/.ssh/allowed_signers
	echo "$GIT_COMMITTER_EMAIL $SSH_PUBLIC_SIGNING_KEY" >~/.ssh/allowed_signers
	git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
fi

# Run Semantic Release
/semantic-release/.venv/bin/python \
	-m semantic_release ${ROOT_OPTIONS} version ${ARGS[@]}
