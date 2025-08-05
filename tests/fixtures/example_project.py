from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Generator, cast
from unittest import mock

import pytest
import tomlkit

# NOTE: use backport with newer API
from importlib_resources import files

import semantic_release
from semantic_release.cli.config import (
    GlobalCommandLineOptions,
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.util import load_raw_config_file
from semantic_release.commit_parser import (
    ConventionalCommitParser,
    EmojiCommitParser,
    ScipyCommitParser,
)
from semantic_release.commit_parser.conventional.parser_monorepo import (
    ConventionalCommitMonorepoParser,
)
from semantic_release.hvcs import Bitbucket, Gitea, Github, Gitlab

import tests.conftest
import tests.const
import tests.util
from tests.const import (
    EXAMPLE_CHANGELOG_MD_CONTENT,
    EXAMPLE_CHANGELOG_RST_CONTENT,
    EXAMPLE_PROJECT_NAME,
    EXAMPLE_PROJECT_VERSION,
    EXAMPLE_PYPROJECT_TOML_CONTENT,
    EXAMPLE_RELEASE_NOTES_TEMPLATE,
    EXAMPLE_SETUP_CFG_CONTENT,
    EXAMPLE_SETUP_PY_CONTENT,
)
from tests.util import copy_dir_tree, temporary_working_directory

if TYPE_CHECKING:
    from typing import Any, Protocol, Sequence

    from tomlkit.container import Container as TOMLContainer

    from semantic_release.commit_parser import CommitParser
    from semantic_release.commit_parser._base import ParserOptions
    from semantic_release.commit_parser.token import ParseResult
    from semantic_release.hvcs import HvcsBase
    from semantic_release.version.version import Version

    from tests.conftest import (
        BuildRepoOrCopyCacheFn,
        GetMd5ForSetOfFilesFn,
    )
    from tests.fixtures.git_repo import RepoActions

    ExProjectDir = Path

    class GetWheelFileFn(Protocol):
        def __call__(self, version_str: str, pkg_name: str = ...) -> Path: ...

    class SetFlagFn(Protocol):
        def __call__(self, flag: bool, toml_file: Path | str = ...) -> None: ...

    class UpdatePyprojectTomlFn(Protocol):
        def __call__(
            self, setting: str, value: Any, toml_file: Path | str = ...
        ) -> None: ...

    class UseCustomParserFn(Protocol):
        def __call__(
            self, module_import_str: str, toml_file: Path | str = ...
        ) -> None: ...

    class UseHvcsFn(Protocol):
        def __call__(
            self, domain: str | None = None, toml_file: Path | str = ...
        ) -> type[HvcsBase]: ...

    class UseParserFn(Protocol):
        def __call__(
            self, toml_file: Path | str = ..., monorepo: bool = ...
        ) -> type[CommitParser[ParseResult, ParserOptions]]: ...

    class UseReleaseNotesTemplateFn(Protocol):
        def __call__(self, toml_file: Path | str = ...) -> None: ...

    class UpdateVersionPyFileFn(Protocol):
        def __call__(
            self, version: Version | str, version_file: Path | str = ...
        ) -> None: ...

    class GetHvcsFn(Protocol):
        def __call__(
            self,
            hvcs_client_name: str,
            origin_url: str = ...,
            hvcs_domain: str | None = None,
        ) -> Github | Gitlab | Gitea | Bitbucket: ...

    class ReadConfigFileFn(Protocol):
        """Read the raw config file from `config_path`."""

        def __call__(self, file: Path | str = ...) -> RawConfig: ...

    class LoadRuntimeContextFn(Protocol):
        """Load the runtime context from the config file."""

        def __call__(
            self, cli_opts: GlobalCommandLineOptions | None = None
        ) -> RuntimeContext: ...

    class GetParserFromConfigFileFn(Protocol):
        """Get the commit parser from the config file."""

        def __call__(
            self, file: Path | str = ...
        ) -> CommitParser[ParseResult, ParserOptions]: ...

    class GetExpectedVersionPyFileContentFn(Protocol):
        def __call__(self, version: Version | str) -> str: ...


@pytest.fixture(scope="session")
def deps_files_4_example_project() -> list[Path]:
    return [
        # This file
        Path(__file__).absolute(),
        # because of imports
        Path(tests.const.__file__).absolute(),
        Path(tests.util.__file__).absolute(),
        # because of the fixtures
        Path(tests.conftest.__file__).absolute(),
    ]


@pytest.fixture(scope="session")
def build_spec_hash_4_example_project(
    get_md5_for_set_of_files: GetMd5ForSetOfFilesFn,
    deps_files_4_example_project: list[Path],
) -> str:
    # Generates a hash of the build spec to set when to invalidate the cache
    return get_md5_for_set_of_files(deps_files_4_example_project)


@pytest.fixture(scope="session")
def cached_example_project(
    build_repo_or_copy_cache: BuildRepoOrCopyCacheFn,
    version_py_file: Path,
    pyproject_toml_file: Path,
    setup_cfg_file: Path,
    setup_py_file: Path,
    changelog_md_file: Path,
    changelog_rst_file: Path,
    build_spec_hash_4_example_project: str,
    update_version_py_file: UpdateVersionPyFileFn,
) -> Path:
    """
    Initializes the example project. DO NOT USE DIRECTLY

    Use the `init_example_project` fixture instead.
    """

    def _build_project(cached_project_path: Path) -> Sequence[RepoActions]:
        # purposefully a relative path
        example_dir = version_py_file.parent
        gitignore_contents = dedent(
            f"""
            *.pyc
            /src/**/{version_py_file.name}
            """
        ).lstrip()
        init_py_contents = dedent(
            '''
            """
            An example package with a very informative docstring
            """
            from ._version import __version__


            def hello_world() -> None:
                print("Hello World")
            '''
        ).lstrip()

        with temporary_working_directory(cached_project_path):
            update_version_py_file(EXAMPLE_PROJECT_VERSION)

        file_2_contents: list[tuple[str | Path, str]] = [
            (example_dir / "__init__.py", init_py_contents),
            (".gitignore", gitignore_contents),
            (pyproject_toml_file, EXAMPLE_PYPROJECT_TOML_CONTENT),
            (setup_cfg_file, EXAMPLE_SETUP_CFG_CONTENT),
            (setup_py_file, EXAMPLE_SETUP_PY_CONTENT),
            (changelog_md_file, EXAMPLE_CHANGELOG_MD_CONTENT),
            (changelog_rst_file, EXAMPLE_CHANGELOG_RST_CONTENT),
        ]

        for file, contents in file_2_contents:
            abs_filepath = cached_project_path.joinpath(file).resolve()
            # make sure the parent directory exists
            abs_filepath.parent.mkdir(parents=True, exist_ok=True)
            # write file contents
            abs_filepath.write_text(contents)

        # This is a special build, we don't expose the Repo Actions to the caller
        return []

    # End of _build_project()

    return build_repo_or_copy_cache(
        repo_name=f"project_{EXAMPLE_PROJECT_NAME}",
        build_spec_hash=build_spec_hash_4_example_project,
        build_repo_func=_build_project,
    )


@pytest.fixture
def init_example_project(
    example_project_dir: ExProjectDir,
    cached_example_project: Path,
    change_to_ex_proj_dir: None,
) -> None:
    """This fixture initializes the example project in the current test's project directory."""
    if not cached_example_project.exists():
        raise RuntimeError(
            f"Unable to find cached project files for {EXAMPLE_PROJECT_NAME}"
        )

    # Copy the cached project files into the current test's project directory
    copy_dir_tree(cached_example_project, example_project_dir)


@pytest.fixture
def example_project_with_release_notes_template(
    init_example_project: None,
    use_release_notes_template: UseReleaseNotesTemplateFn,
) -> None:
    use_release_notes_template()


@pytest.fixture(scope="session")
def version_py_file() -> Path:
    return Path("src", EXAMPLE_PROJECT_NAME, "_version.py")


@pytest.fixture(scope="session")
def pyproject_toml_file() -> Path:
    return Path("pyproject.toml")


@pytest.fixture(scope="session")
def setup_cfg_file() -> Path:
    return Path("setup.cfg")


@pytest.fixture(scope="session")
def setup_py_file() -> Path:
    return Path("setup.py")


@pytest.fixture(scope="session")
def dist_dir() -> Path:
    return Path("dist")


@pytest.fixture(scope="session")
def changelog_md_file() -> Path:
    return Path("CHANGELOG.md")


@pytest.fixture(scope="session")
def changelog_rst_file() -> Path:
    return Path("CHANGELOG.rst")


@pytest.fixture(scope="session")
def changelog_template_dir() -> Path:
    return Path("templates")


@pytest.fixture(scope="session")
def default_md_changelog_insertion_flag() -> str:
    return "<!-- version list -->"


@pytest.fixture(scope="session")
def default_rst_changelog_insertion_flag() -> str:
    return f"..{os.linesep}    version list"


@pytest.fixture(scope="session")
def default_changelog_md_template() -> Path:
    """Retrieve the semantic-release default changelog template file"""
    return Path(
        str(
            files(semantic_release.__name__).joinpath(
                Path("data", "templates", "conventional", "md", "CHANGELOG.md.j2")
            )
        )
    ).resolve()


@pytest.fixture(scope="session")
def default_changelog_rst_template() -> Path:
    """Retrieve the semantic-release default changelog template file"""
    return Path(
        str(
            files(semantic_release.__name__).joinpath(
                Path("data", "templates", "conventional", "rst", "CHANGELOG.rst.j2")
            )
        )
    ).resolve()


@pytest.fixture(scope="session")
def get_wheel_file(dist_dir: Path) -> GetWheelFileFn:
    def _get_wheel_file(
        version_str: str,
        pkg_name: str = EXAMPLE_PROJECT_NAME,
    ) -> Path:
        return dist_dir.joinpath(
            f"{pkg_name.replace('-', '_')}-{version_str}-py3-none-any.whl"
        )

    return _get_wheel_file


@pytest.fixture(scope="session")
def read_config_file(pyproject_toml_file: Path) -> ReadConfigFileFn:
    def _read_config_file(file: Path | str = pyproject_toml_file) -> RawConfig:
        config_text = load_raw_config_file(file)
        return RawConfig.model_validate(config_text)

    return _read_config_file


@pytest.fixture(scope="session")
def load_runtime_context(
    read_config_file: ReadConfigFileFn,
    pyproject_toml_file: Path,
) -> LoadRuntimeContextFn:
    def _load_runtime_context(
        cli_opts: GlobalCommandLineOptions | None = None,
    ) -> RuntimeContext:
        opts = cli_opts or GlobalCommandLineOptions(
            config_file=str(pyproject_toml_file),
        )
        raw_config = read_config_file(opts.config_file)
        return RuntimeContext.from_raw_config(raw_config, opts)

    return _load_runtime_context


@pytest.fixture(scope="session")
def get_parser_from_config_file(
    pyproject_toml_file: Path,
    load_runtime_context: LoadRuntimeContextFn,
) -> GetParserFromConfigFileFn:
    def _get_parser_from_config(
        file: Path | str = pyproject_toml_file,
    ) -> CommitParser[ParseResult, ParserOptions]:
        return load_runtime_context(
            cli_opts=GlobalCommandLineOptions(config_file=str(Path(file)))
        ).commit_parser

    return _get_parser_from_config


@pytest.fixture
def example_project_dir(tmp_path: Path) -> ExProjectDir:
    return tmp_path.resolve()


@pytest.fixture
def change_to_ex_proj_dir(
    example_project_dir: ExProjectDir,
) -> Generator[None, None, None]:
    cwd = os.getcwd()
    tgt_dir = str(example_project_dir.resolve())
    if cwd == tgt_dir:
        return

    os.chdir(tgt_dir)
    try:
        yield
    finally:
        os.chdir(cwd)


@pytest.fixture
def use_release_notes_template(
    example_project_template_dir: Path,
    changelog_template_dir: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_file: Path,
) -> UseReleaseNotesTemplateFn:
    def _use_release_notes_template(
        toml_file: Path | str = pyproject_toml_file,
    ) -> None:
        update_pyproject_toml(
            "tool.semantic_release.changelog.template_dir",
            str(changelog_template_dir),
            toml_file=toml_file,
        )
        example_project_template_dir.mkdir(parents=True, exist_ok=True)
        release_notes_j2 = example_project_template_dir / ".release_notes.md.j2"
        release_notes_j2.write_text(EXAMPLE_RELEASE_NOTES_TEMPLATE)

    return _use_release_notes_template


@pytest.fixture
def example_pyproject_toml(
    example_project_dir: ExProjectDir,
    pyproject_toml_file: Path,
) -> Path:
    return example_project_dir / pyproject_toml_file


@pytest.fixture
def example_setup_cfg(
    example_project_dir: ExProjectDir,
    setup_cfg_file: Path,
) -> Path:
    return example_project_dir / setup_cfg_file


@pytest.fixture
def example_setup_py(
    example_project_dir: ExProjectDir,
    setup_py_file: Path,
) -> Path:
    return example_project_dir / setup_py_file


@pytest.fixture
def example_dist_dir(
    example_project_dir: ExProjectDir,
    dist_dir: Path,
) -> Path:
    return example_project_dir / dist_dir


@pytest.fixture
def example_project_wheel_file(
    example_dist_dir: Path,
    get_wheel_file: GetWheelFileFn,
) -> Path:
    return example_dist_dir / get_wheel_file(EXAMPLE_PROJECT_VERSION)


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_md(
    example_project_dir: ExProjectDir,
    changelog_md_file: Path,
) -> Path:
    return example_project_dir / changelog_md_file


# Note this is just the path and the content may change
@pytest.fixture
def example_changelog_rst(
    example_project_dir: ExProjectDir,
    changelog_rst_file: Path,
) -> Path:
    return example_project_dir / changelog_rst_file


@pytest.fixture
def example_project_template_dir(
    example_project_dir: ExProjectDir,
    changelog_template_dir: Path,
) -> Path:
    return example_project_dir / changelog_template_dir


@pytest.fixture(scope="session")
def get_expected_version_py_file_content() -> GetExpectedVersionPyFileContentFn:
    def _get_expected_version_py_file_content(version: Version | str) -> str:
        return dedent(
            f"""\
            __version__ = "{version}"
            """
        )

    return _get_expected_version_py_file_content


@pytest.fixture(scope="session")
def update_version_py_file(
    version_py_file: Path,
    get_expected_version_py_file_content: GetExpectedVersionPyFileContentFn,
) -> UpdateVersionPyFileFn:
    """
    Updates the specified file with the expected version string content

    :param version: The version to set in the file
    :type version: Version | str

    :param version_file: The file to update
    :type version_file: Path | str
    """

    def _update_version_py_file(
        version: Version | str, version_file: Path | str = version_py_file
    ) -> None:
        cwd_version_py = Path(version_file).resolve()
        cwd_version_py.parent.mkdir(parents=True, exist_ok=True)
        cwd_version_py.write_text(get_expected_version_py_file_content(version))

    return _update_version_py_file


@pytest.fixture(scope="session")
def update_pyproject_toml(pyproject_toml_file: Path) -> UpdatePyprojectTomlFn:
    """Update the pyproject.toml file with the given content."""

    def _update_pyproject_toml(
        setting: str, value: Any, toml_file: Path | str = pyproject_toml_file
    ) -> None:
        cwd_pyproject_toml = Path(toml_file).resolve()
        with open(cwd_pyproject_toml) as rfd:
            pyproject_toml = tomlkit.load(rfd)

        new_setting = {}
        parts = setting.split(".")
        new_setting_key = parts.pop(-1)
        new_setting[new_setting_key] = value

        pointer: TOMLContainer = pyproject_toml
        for part in parts:
            if (next_pointer := pointer.get(part, None)) is None:
                next_pointer = tomlkit.table()
                pointer.add(part, next_pointer)

            pointer = cast("TOMLContainer", next_pointer)

        if value is None:
            pointer.pop(new_setting_key)
        else:
            pointer.update(new_setting)

        with open(cwd_pyproject_toml, "w") as wfd:
            tomlkit.dump(pyproject_toml, wfd)

    return _update_pyproject_toml


@pytest.fixture(scope="session")
def pyproject_toml_config_option_parser() -> str:
    return f"tool.{semantic_release.__name__}.commit_parser"


@pytest.fixture(scope="session")
def pyproject_toml_config_option_remote_type() -> str:
    return f"tool.{semantic_release.__name__}.remote.type"


@pytest.fixture(scope="session")
def pyproject_toml_config_option_remote_domain() -> str:
    return f"tool.{semantic_release.__name__}.remote.domain"


@pytest.fixture(scope="session")
def set_major_on_zero(
    pyproject_toml_file: Path, update_pyproject_toml: UpdatePyprojectTomlFn
) -> SetFlagFn:
    """Turn on/off the major_on_zero setting."""

    def _set_major_on_zero(
        flag: bool, toml_file: Path | str = pyproject_toml_file
    ) -> None:
        update_pyproject_toml("tool.semantic_release.major_on_zero", flag, toml_file)

    return _set_major_on_zero


@pytest.fixture(scope="session")
def set_allow_zero_version(
    pyproject_toml_file: Path, update_pyproject_toml: UpdatePyprojectTomlFn
) -> SetFlagFn:
    """Turn on/off the allow_zero_version setting."""

    def _set_allow_zero_version(
        flag: bool, toml_file: Path | str = pyproject_toml_file
    ) -> None:
        update_pyproject_toml(
            "tool.semantic_release.allow_zero_version", flag, toml_file
        )

    return _set_allow_zero_version


@pytest.fixture(scope="session")
def use_conventional_parser(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Conventional parser."""

    def _use_conventional_parser(
        toml_file: Path | str = pyproject_toml_file, monorepo: bool = False
    ) -> type[CommitParser[ParseResult, ParserOptions]]:
        update_pyproject_toml(
            pyproject_toml_config_option_parser,
            f"conventional{'-monorepo' if monorepo else ''}",
            toml_file=toml_file,
        )
        return cast(
            "type[CommitParser[ParseResult, ParserOptions]]",
            ConventionalCommitMonorepoParser if monorepo else ConventionalCommitParser,
        )

    return _use_conventional_parser


@pytest.fixture(scope="session")
def use_emoji_parser(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Emoji parser."""

    def _use_emoji_parser(
        toml_file: Path | str = pyproject_toml_file, monorepo: bool = False
    ) -> type[CommitParser[ParseResult, ParserOptions]]:
        if monorepo:
            raise ValueError(
                "The Emoji parser does not support monorepo mode. "
                "Use the conventional parser instead."
            )

        update_pyproject_toml(
            pyproject_toml_config_option_parser, "emoji", toml_file=toml_file
        )
        return cast("type[CommitParser[ParseResult, ParserOptions]]", EmojiCommitParser)

    return _use_emoji_parser


@pytest.fixture(scope="session")
def use_scipy_parser(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseParserFn:
    """Modify the configuration file to use the Scipy parser."""

    def _use_scipy_parser(
        toml_file: Path | str = pyproject_toml_file, monorepo: bool = False
    ) -> type[CommitParser[ParseResult, ParserOptions]]:
        if monorepo:
            raise ValueError(
                "The Scipy parser does not support monorepo mode. "
                "Use the conventional parser instead."
            )

        update_pyproject_toml(
            pyproject_toml_config_option_parser, "scipy", toml_file=toml_file
        )
        return cast("type[CommitParser[ParseResult, ParserOptions]]", ScipyCommitParser)

    return _use_scipy_parser


@pytest.fixture(scope="session")
def use_custom_parser(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_parser: str,
) -> UseCustomParserFn:
    """Modify the configuration file to use a user defined string parser."""

    def _use_custom_parser(
        module_import_str: str, toml_file: Path | str = pyproject_toml_file
    ) -> None:
        update_pyproject_toml(
            pyproject_toml_config_option_parser, module_import_str, toml_file=toml_file
        )

    return _use_custom_parser


@pytest.fixture(scope="session")
def get_hvcs(example_git_https_url: str) -> GetHvcsFn:
    hvcs_clients: dict[str, type[HvcsBase]] = {
        "github": Github,
        "gitlab": Gitlab,
        "gitea": Gitea,
        "bitbucket": Bitbucket,
    }

    def _get_hvcs(
        hvcs_client_name: str,
        origin_url: str = example_git_https_url,
        hvcs_domain: str | None = None,
    ) -> Github | Gitlab | Gitea | Bitbucket:
        if (hvcs_class := hvcs_clients.get(hvcs_client_name)) is None:
            raise ValueError(f"Unknown HVCS client name: {hvcs_client_name}")

        # Create HVCS Client instance
        with mock.patch.dict(os.environ, {}, clear=True):
            hvcs = hvcs_class(origin_url, hvcs_domain=hvcs_domain)
            assert hvcs.repo_name  # Force the HVCS client to cache the repo name
            assert hvcs.owner  # Force the HVCS client to cache the owner

        return cast("Github | Gitlab | Gitea | Bitbucket", hvcs)

    return _get_hvcs


@pytest.fixture(scope="session")
def use_github_hvcs(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_remote_type: str,
    pyproject_toml_config_option_remote_domain: str,
) -> UseHvcsFn:
    """Modify the configuration file to use GitHub as the HVCS."""

    def _use_github_hvcs(
        domain: str | None = None, toml_file: Path | str = pyproject_toml_file
    ) -> type[HvcsBase]:
        update_pyproject_toml(
            pyproject_toml_config_option_remote_type,
            Github.__name__.lower(),
            toml_file=toml_file,
        )

        if domain is not None:
            update_pyproject_toml(
                pyproject_toml_config_option_remote_domain, domain, toml_file=toml_file
            )

        return Github

    return _use_github_hvcs


@pytest.fixture(scope="session")
def use_gitlab_hvcs(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_remote_type: str,
    pyproject_toml_config_option_remote_domain: str,
) -> UseHvcsFn:
    """Modify the configuration file to use GitLab as the HVCS."""

    def _use_gitlab_hvcs(
        domain: str | None = None, toml_file: Path | str = pyproject_toml_file
    ) -> type[HvcsBase]:
        update_pyproject_toml(
            pyproject_toml_config_option_remote_type,
            Gitlab.__name__.lower(),
            toml_file=toml_file,
        )

        if domain is not None:
            update_pyproject_toml(
                pyproject_toml_config_option_remote_domain, domain, toml_file=toml_file
            )

        return Gitlab

    return _use_gitlab_hvcs


@pytest.fixture(scope="session")
def use_gitea_hvcs(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_remote_type: str,
    pyproject_toml_config_option_remote_domain: str,
) -> UseHvcsFn:
    """Modify the configuration file to use Gitea as the HVCS."""

    def _use_gitea_hvcs(
        domain: str | None = None, toml_file: Path | str = pyproject_toml_file
    ) -> type[HvcsBase]:
        update_pyproject_toml(
            pyproject_toml_config_option_remote_type,
            Gitea.__name__.lower(),
            toml_file=toml_file,
        )

        if domain is not None:
            update_pyproject_toml(
                pyproject_toml_config_option_remote_domain, domain, toml_file=toml_file
            )

        return Gitea

    return _use_gitea_hvcs


@pytest.fixture(scope="session")
def use_bitbucket_hvcs(
    pyproject_toml_file: Path,
    update_pyproject_toml: UpdatePyprojectTomlFn,
    pyproject_toml_config_option_remote_type: str,
    pyproject_toml_config_option_remote_domain: str,
) -> UseHvcsFn:
    """Modify the configuration file to use BitBucket as the HVCS."""

    def _use_bitbucket_hvcs(
        domain: str | None = None, toml_file: Path | str = pyproject_toml_file
    ) -> type[HvcsBase]:
        update_pyproject_toml(
            pyproject_toml_config_option_remote_type,
            Bitbucket.__name__.lower(),
            toml_file=toml_file,
        )

        if domain is not None:
            update_pyproject_toml(
                pyproject_toml_config_option_remote_domain, domain, toml_file=toml_file
            )

        return Bitbucket

    return _use_bitbucket_hvcs
