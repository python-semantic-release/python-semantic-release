#!/bin/bash

set -eu -o pipefail

function load_env() {
    set -eu -o pipefail

    if [ "${UTILITIES_SH_LOADED:-false}" = "false" ]; then
        local __FILE__=""
        __FILE__="$(realpath "${BASH_SOURCE[0]}")"

        local __DIR__=""
        __DIR__="$(realpath "$(dirname "$__FILE__")")"

        local ROOT_DIR=""
        ROOT_DIR="$(realpath "$(dirname "$__DIR__")")"

        # shellcheck source=scripts/utils.sh
        source "$ROOT_DIR/scripts/utils.sh"

        load_base_env
    fi
}

function with_temp_working_dir() {
    local working_dir="${1:?"Working directory not specified, but is required!"}"
    pushd "$working_dir" >/dev/null || return 1
    explicit_run_cmd "${@:2}" || return 1
    popd >/dev/null || return 1
}

function build_sdist() {
    local status_msg="${1:?"Status message not specified, but is required!"}"
    local output_dir="${2:?"Output directory not specified, but is required!"}"

    if ! explicit_run_cmd_w_status_wrapper \
        "$status_msg" \
        python3 -m build --sdist . --outdir "$output_dir" ">/dev/null";
    then
        return 1
    fi
    find "$output_dir" -type f -name "*.tar.gz" -exec \
        sh -c 'printf "%s\n" "Successfully built $1"' shell {} \;
}

function unpack_sdist() {
    local sdist_file="${1:?"Source distribution file not specified, but is required!"}"
    local output_dir="${2:?"Output directory not specified, but is required!"}"

    mkdir -p "$output_dir"
    if ! explicit_run_cmd_w_status_wrapper \
        "Unpacking sdist code into '$output_dir'" \
        tar -xzf "$sdist_file" -C "$output_dir" --strip-components=1;
    then
        return 1
    fi
}


function strip_optional_dependencies {
    local -r pyproject_file="${1:?'param[1]: Path to pyproject.toml file is required'}"
    local -r exclude_groups=("${@:2}")
    local python_snippet="\
        from pathlib import Path
        from sys import argv, exit
        try:
            import tomlkit
        except ModuleNotFoundError:
            print('Failed Import: Missing build requirement \'tomlkit\'.')
            exit(1)

        pyproject_file = Path(argv[1])
        config = tomlkit.loads(pyproject_file.read_text())
        proj_config = config.get('project', {})

        if not (opt_deps := proj_config.get('optional-dependencies', {})):
            exit(0)

        if not (dep_group_to_remove := argv[2:]):
            exit(0)

        for group in dep_group_to_remove:
            if group in opt_deps:
                opt_deps.pop(group)

        if not opt_deps:
            proj_config.pop('optional-dependencies')

        pyproject_file.write_text(tomlkit.dumps(config))
    "
    # make whitespace nice for python (remove indent)
    python_snippet="$(printf '%s\n' "$python_snippet" | sed -E 's/([ ]{4,8}|\t)(.*)/\2/')"

    if [ "${#exclude_groups[@]}" -eq 0 ]; then
        error "At least one dependency group to exclude must be specified!"
        return 1
    fi

    python3 -c "$python_snippet" "$pyproject_file" "${exclude_groups[@]}" || return 1
}

remove_empty_init_files() {
    local dirpath="${1:-.}"

    # SNIPPET: Remove empty __init__.py files
    local python_snippet='\
        from pathlib import Path
        from sys import exit, argv, stderr

        if len(argv) < 2 or not (dirpath := Path(argv[1])).is_dir():
            print("Usage: <existing_dirpath>", file=stderr)
            exit(1)

        for filepath in dirpath.resolve().rglob("__init__.py"):
            if not filepath.is_file():
                continue
            if not filepath.read_text().strip():
                filepath.unlink()
                print(f"Removed {filepath}")
    '
    # make whitespace nice for python
    python_snippet="$(printf '%s\n' "$python_snippet" | sed -E 's/([ ]{4,8}|\t)(.*)/\2/')"

    python3 -c "$python_snippet" "$dirpath" || return 1
}

function build_production_whl() {
    # Assumes the current working directory is the directory to modify
    local dest_dir="${1:?"param[1]: output directory not specified, but required!"}"

    # Strip out development dependencies
    explicit_run_cmd_w_status_wrapper \
        "Masking development dependencies" \
        strip_optional_dependencies "pyproject.toml" "build" "dev" "docs" "test" "mypy" || return 1

    # Optimize code for runtime
    explicit_run_cmd_w_status_wrapper \
        "Removing empty '__init__.py' files" \
        remove_empty_init_files "src" || return 1

    # Remove editable info from the source directory before wheel build
    rm -rf src/*.egg-info/

    # Build the wheel into the output directory
    explicit_run_cmd_w_status_wrapper \
        "Constructing wheel package" \
        python3 -m build --wheel . --outdir "$dest_dir" || return 1
}

function build_wheel_from_sdist() {
    local build_dir="${1:?"param[1]: Build directory not specified, but is required!"}"
    local dest_dir="${2:?"param[2]: Output directory not specified, but is required!"}"
    local tmp_src_dir="$build_dir/sdist"

    unpack_sdist "$build_dir/*.tar.gz" "$tmp_src_dir" || return 1

    with_temp_working_dir "$tmp_src_dir" build_production_whl "$dest_dir" || return 1

    rm -rf "$tmp_src_dir"
}

function build_production_package() {
    local dest_dir
    local output_dir="${1:?"param[1]: Output directory not specified, but required!"}"
    local build_dir="build"

    # If the output directory is not an absolute path, make it absolute
    if ! stdout "$output_dir" | grep -q -E '^/'; then
        dest_dir="$(realpath ".")/$output_dir"
    else
        dest_dir="$output_dir"
    fi

    # Clean up any existing output directory
    if [ -d "$dest_dir" ]; then
        rm -rf "$dest_dir"
    fi

    # Clean up any existing build directory
    if [ -d "$build_dir" ]; then
        rm -rf "$build_dir"
    fi

    build_sdist "Bundling source code" "$build_dir" || return 1

    explicit_run_cmd_w_status_wrapper \
        "Building production wheel from sdist" \
        build_wheel_from_sdist "$build_dir" "$dest_dir" || return 1

    rm -rf "$build_dir"
}

function main() {
    set -eu -o pipefail

    cd "$PROJ_ROOT_DIR"

    if ! explicit_run_cmd_w_status_wrapper \
        "Verifying Python environment" \
        verify_python "$MINIMUM_PYTHON_VERSION";
    then
        info "Please run the dev setup script and activate the virtual environment first."
        return 1
    fi

    explicit_run_cmd_w_status_wrapper \
        "Verifying build dependencies exist" \
        python3 -m pip install -e ".[build]" ">/dev/null"

    explicit_run_cmd_w_status_wrapper \
        "Building production package" \
        build_production_package "dist"
}

########################################################################
# CONDITIONAL AUTO-EXECUTE                                             #
########################################################################

if ! (return 0 2>/dev/null); then
    # Since this script is not being sourced, run the main function
    unset -v UTILITIES_SH_LOADED  # Ensure utils are reloaded when called from another script
    load_env
    main "$@"
fi
