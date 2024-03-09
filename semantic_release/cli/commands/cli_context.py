from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import click
from click.core import ParameterSource
from git import InvalidGitRepositoryError
from pydantic import ValidationError

from semantic_release.cli.config import (
    RawConfig,
    RuntimeContext,
)
from semantic_release.cli.util import load_raw_config_file, rprint
from semantic_release.errors import InvalidConfiguration, NotAReleaseBranch

if TYPE_CHECKING:
    from semantic_release.cli.config import GlobalCommandLineOptions

    class CliContext(click.Context):
        obj: CliContextObj


class CliContextObj:
    def __init__(
        self,
        ctx: click.Context,
        logger: logging.Logger,
        global_opts: GlobalCommandLineOptions,
    ) -> None:
        self._runtime_ctx: RuntimeContext | None = None
        self.ctx = ctx
        self.logger = logger
        self.global_opts = global_opts

    @property
    def runtime_ctx(self) -> RuntimeContext:
        """
        Lazy load the runtime context. This is done to avoid configuration loading when
        the command is not run. This is useful for commands like `--help` and `--version`
        """
        if self._runtime_ctx is None:
            self._runtime_ctx = self._init_runtime_ctx()
        return self._runtime_ctx

    def _init_runtime_ctx(self) -> RuntimeContext:
        config_path = Path(self.global_opts.config_file)
        conf_file_exists = config_path.exists()
        was_conf_file_user_provided = bool(
            self.ctx.get_parameter_source("config_file")
            not in (
                ParameterSource.DEFAULT,
                ParameterSource.DEFAULT_MAP,
            )
        )

        try:
            if was_conf_file_user_provided and not conf_file_exists:
                raise FileNotFoundError(
                    f"File {self.global_opts.config_file} does not exist"
                )

            config_obj = (
                {} if not conf_file_exists else load_raw_config_file(config_path)
            )
            if not config_obj:
                self.logger.info(
                    "configuration empty, falling back to default configuration"
                )

            raw_config = RawConfig.model_validate(config_obj)
            runtime = RuntimeContext.from_raw_config(
                raw_config,
                global_cli_options=self.global_opts,
            )
        except NotAReleaseBranch as exc:
            rprint(f"[bold {'red' if self.global_opts.strict else 'orange1'}]{exc!s}")
            # If not strict, exit 0 so other processes can continue. For example, in
            # multibranch CI it might be desirable to run a non-release branch's pipeline
            # without specifying conditional execution of PSR based on branch name
            self.ctx.exit(2 if self.global_opts.strict else 0)
        except FileNotFoundError as exc:
            click.echo(str(exc), err=True)
            self.ctx.exit(2)
        except (
            ValidationError,
            InvalidConfiguration,
            InvalidGitRepositoryError,
        ) as exc:
            click.echo(str(exc), err=True)
            self.ctx.exit(1)

        # This allows us to mask secrets in the logging
        # by applying it to all the configured handlers
        for handler in logging.getLogger().handlers:
            handler.addFilter(runtime.masker)

        return runtime
