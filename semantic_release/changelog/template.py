import importlib
from typing import Any, Callable, Iterable, Optional, Union

from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from typing_extensions import Literal


def _dynamic_import(import_path: str) -> Any:
    module_name, _, attr = import_path.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


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
    Create a jinja2.Environment with certain parameter resrictions;
    for example the Loader is fixed to FileSystemLoader, although the searchpath
    is configurable.

    ``autoescape`` can be a string in which case it should follow the convention
    ``module:attr``, in this instance it will be dynamically imported.
    See https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment for full
    parameter descriptions
    """
    autoescape_value: Union[bool, Callable[[Optional[str]], bool]]
    if isinstance(autoescape, str):
        autoescape_value = _dynamic_import(autoescape)  # type: ignore
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
