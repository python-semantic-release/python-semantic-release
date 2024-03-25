#!/bin/bash

set -e

# Convert "true"/"false" into command line args
eval_boolean_action_input() {
	local -r input_name="$1"
	shift
	local -r flag_value="$1"
	shift
	local -r if_true="$1"
	shift
	local -r if_false="$1"

	if [ "$flag_value" = "true" ]; then
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
source ~/semantic-release/.venv/bin/activate
export GIT_COMMIT_AUTHOR="${GIT_COMMITTER_NAME} <${GIT_COMMITTER_EMAIL}>"

# Convert inputs to command line arguments
export ARGS=()
ARGS+=("$(eval_boolean_action_input "prerelease" "$PRERELEASE" "--prerelease" "")") || exit 1
ARGS+=("$(eval_boolean_action_input "commit" "$COMMIT" "--commit" "--no-commit")") || exit 1
ARGS+=("$(eval_boolean_action_input "push" "$PUSH" "--push" "--no-push")") || exit 1
ARGS+=("$(eval_boolean_action_input "changelog" "$CHANGELOG" "--changelog" "--no-changelog")") || exit 1
ARGS+=("$(eval_boolean_action_input "vcs_release" "$VCS_RELEASE" "--vcs-release" "--no-vcs-release")") || exit 1

# Handle --patch, --minor, --major
# https://stackoverflow.com/a/47541882
valid_force_levels=("patch" "minor" "major")
if [ -z "$FORCE" ]; then
	true # do nothing if 'force' input is not set
elif printf '%s\0' "${valid_force_levels[@]}" | grep -Fxzq "$FORCE"; then
	ARGS+=("--$FORCE")
else
	printf "Error: Input 'force' must be one of: %s\n" "${valid_force_levels[@]}" >&2
fi

if [ -n "$BUILD_METADATA" ]; then
	ARGS+=("--build-metadata $BUILD_METADATA")
fi

# Change to configured directory
cd "${DIRECTORY}"

# Set Git details
git config user.name "$GIT_COMMITTER_NAME"
git config user.email "$GIT_COMMITTER_EMAIL"

if [[ -n $SSH_PUBLIC_SIGNING_KEY && -n $SSH_PRIVATE_SIGNING_KEY ]]; then
	echo "SSH Key pair found, configuring signing..."
	mkdir ~/.ssh
	echo -e "$SSH_PRIVATE_SIGNING_KEY" >>~/.ssh/signing_key
	cat ~/.ssh/signing_key
	echo -e "$SSH_PUBLIC_SIGNING_KEY" >>~/.ssh/signing_key.pub
	cat ~/.ssh/signing_key.pub
	chmod 600 ~/.ssh/signing_key && chmod 600 ~/.ssh/signing_key.pub
	eval "$(ssh-agent)"
	ssh-add ~/.ssh/signing_key
	git config gpg.format ssh
	git config user.signingKey ~/.ssh/signing_key
	git config commit.gpgsign true
	git config user.email $GIT_COMMITTER_EMAIL
	git config user.name $GIT_COMMITTER_NAME
	touch ~/.ssh/allowed_signers
	echo "$GIT_COMMITTER_EMAIL $SSH_PUBLIC_SIGNING_KEY" >~/.ssh/allowed_signers
	git config gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
fi

# Run Semantic Release
~/semantic-release/.venv/bin/python \
	-m semantic_release ${ROOT_OPTIONS} version ${ARGS[@]}
