from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Callable, Iterable

from jinja2 import Environment, FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from typing_extensions import Literal

from semantic_release.helpers import dynamic_import

log = logging.getLogger(__name__)


# pylint: disable=too-many-arguments,too-many-locals
def environment(
    template_dir: str = ".",
    block_start_string: str = "{%",
    block_end_string: str = "%}",
    variable_start_string: str = "{{",
    variable_end_string: str = "}}",
    comment_start_string: str = "{#",
    comment_end_string: str = "#}",
    line_statement_prefix: str | None = None,
    line_comment_prefix: str | None = None,
    trim_blocks: bool = False,
    lstrip_blocks: bool = False,
    newline_sequence: Literal["\n", "\r", "\r\n"] = "\n",
    keep_trailing_newline: bool = False,
    extensions: Iterable[str] = (),
    autoescape: bool | str = True,
) -> SandboxedEnvironment:
    """
    Create a jinja2.sandbox.SandboxedEnvironment with certain parameter resrictions;
    for example the Loader is fixed to FileSystemLoader, although the searchpath
    is configurable.

    ``autoescape`` can be a string in which case it should follow the convention
    ``module:attr``, in this instance it will be dynamically imported.
    See https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment for full
    parameter descriptions
    """
    autoescape_value: bool | Callable[[str | None], bool]
    if isinstance(autoescape, str):
        autoescape_value = dynamic_import(autoescape)
    else:
        autoescape_value = autoescape
    log.debug("%s", locals())

    return SandboxedEnvironment(
        block_start_string=block_start_string,
        block_end_string=block_end_string,
        variable_start_string=variable_start_string,
        variable_end_string=variable_end_string,
        comment_start_string=comment_start_string,
        comment_end_string=comment_end_string,
        line_statement_prefix=line_statement_prefix,
        line_comment_prefix=line_comment_prefix,
        trim_blocks=trim_blocks,
        lstrip_blocks=lstrip_blocks,
        newline_sequence=newline_sequence,
        keep_trailing_newline=keep_trailing_newline,
        extensions=extensions,
        autoescape=autoescape_value,
        loader=FileSystemLoader(template_dir, encoding="utf-8"),
    )


# pylint: disable=redefined-outer-name
def recursive_render(
    template_dir: str, environment: Environment, _root_dir: str = "."
) -> list[str]:
    rendered_paths: list[str] = []
    for root, file in (
        (root, file)
        for root, _, files in os.walk(template_dir)
        for file in files
        if not any(elem.startswith(".") for elem in root.split(os.sep))
        and not file.startswith(".")
    ):
        src_path = Path(root)
        output_path = (_root_dir / src_path.relative_to(template_dir)).resolve()
        log.info("Rendering templates from %s to %s", src_path, output_path)
        os.makedirs(str(output_path), exist_ok=True)
        if file.endswith(".j2"):
            # We know the file ends with .j2 by the filter in the for-loop
            output_filename = file[:-3]
            # Strip off the template directory from the front of the root path -
            # that's the output location relative to the repo root
            src_file_path = str((src_path / file).relative_to(template_dir))
            output_file_path = str((output_path / output_filename).resolve())

            log.debug("rendering %s to %s", src_file_path, output_file_path)
            stream = environment.get_template(src_file_path).stream()

            with open(output_file_path, "wb+") as output_file:
                stream.dump(output_file, encoding="utf-8")

            rendered_paths.append(output_file_path)
        else:
            src_file = str((src_path / file).resolve())
            target_file = str((output_path / file).resolve())
            log.debug(
                "source file %s is not a template, copying to %s", src_file, target_file
            )
            shutil.copyfile(src_file, target_file)
            rendered_paths.append(target_file)
    return rendered_paths


# To avoid confusion on import
del Environment
