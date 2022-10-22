import os
import shutil
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Union

from jinja2 import Environment, FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from typing_extensions import Literal

from semantic_release.helpers import dynamic_import


# pylint: disable=too-many-arguments,too-many-locals
def environment(
    template_dir: str = ".",
    block_start_string: str = "{%",
    block_end_string: str = "%}",
    variable_start_string: str = "{{",
    variable_end_string: str = "}}",
    comment_start_string: str = "{#",
    comment_end_string: str = "#}",
    line_statement_prefix: Optional[str] = None,
    line_comment_prefix: Optional[str] = None,
    trim_blocks: bool = False,
    lstrip_blocks: bool = False,
    newline_sequence: Literal["\n", "\r", "\r\n"] = "\n",
    keep_trailing_newline: bool = False,
    extensions: Iterable[str] = (),
    autoescape: Union[bool, str] = True,
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
    autoescape_value: Union[bool, Callable[[Optional[str]], bool]]
    if isinstance(autoescape, str):
        autoescape_value = dynamic_import(autoescape)  # type: ignore
    else:
        autoescape_value = autoescape

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
) -> None:
    for root, file in (
        (root, file)
        for root, _, files in os.walk(template_dir)
        for file in files
        if not any(elem.startswith(".") for elem in root.split(os.sep))
        and not file.startswith(".")
    ):
        src_path = Path(root)
        output_path = (_root_dir / src_path.relative_to(template_dir)).resolve()
        os.makedirs(str(output_path), exist_ok=True)
        if file.endswith(".j2"):
            # We know the file ends with .j2 by the filter in the for-loop
            output_filename = file[:-3]
            # Strip off the template directory from the front of the root path -
            # that's the output location relative to the repo root
            stream = environment.get_template(
                str((src_path / file).relative_to(template_dir))
            ).stream()

            with open(
                str((output_path / output_filename).resolve()), "wb+"
            ) as output_file:
                stream.dump(output_file, encoding="utf-8")
        else:
            shutil.copyfile(
                str((src_path / file).resolve()), str((output_path / file).resolve())
            )


# To avoid confusion on import
del Environment
