from __future__ import annotations

import os
import shutil
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment

from semantic_release.globals import logger
from semantic_release.helpers import dynamic_import

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable, Iterable, Literal

    from jinja2 import Environment


# pylint: disable=too-many-arguments,too-many-locals
def environment(
    template_dir: Path | str = ".",
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
    Create a jinja2.sandbox.SandboxedEnvironment with certain parameter resrictions.

    For example the Loader is fixed to FileSystemLoader, although the searchpath
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

    return ComplexDirectorySandboxedEnvironment(
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


class ComplexDirectorySandboxedEnvironment(SandboxedEnvironment):
    def join_path(self, template: str, parent: str) -> str:
        """
        Add support for complex directory structures in the template directory.

        This method overrides the default functionality of the SandboxedEnvironment
        where all 'include' keywords expect to be in the same directory as the calling
        template, however this is unintuitive when using a complex directory structure.

        This override simulates the changing of directories when you include the template
        from a child directory. When the child then includes a template, it will make the
        path relative to the child directory rather than the top level template directory.
        """
        # Must be posixpath because jinja only knows how to handle posix path includes
        return str(PurePosixPath(parent).parent / template)


def recursive_render(
    template_dir: Path,
    environment: Environment,
    _root_dir: str | os.PathLike[str] = ".",
) -> list[str]:
    rendered_paths: list[str] = []
    for root, file in (
        (Path(root), file)
        for root, _, files in os.walk(template_dir)
        for file in files
        if not any(
            elem.startswith(".") for elem in Path(root).relative_to(template_dir).parts
        )
        and not file.startswith(".")
    ):
        output_path = (_root_dir / root.relative_to(template_dir)).resolve()
        logger.info("Rendering templates from %s to %s", root, output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        if file.endswith(".j2"):
            # We know the file ends with .j2 by the filter in the for-loop
            output_filename = file[:-3]
            # Strip off the template directory from the front of the root path -
            # that's the output location relative to the repo root
            src_file_path = str((root / file).relative_to(template_dir))
            output_file_path = str((output_path / output_filename).resolve())

            # Although, file stream rendering is possible and preferred in most
            # situations, here it is not desired as you cannot read the previous
            # contents of a file during the rendering of the template. This mechanism
            # is used for inserting into a current changelog. When using stream rendering
            # of the same file, it always came back empty
            logger.debug("rendering %s to %s", src_file_path, output_file_path)
            rendered_file = environment.get_template(src_file_path).render().rstrip()
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(f"{rendered_file}\n")

            rendered_paths.append(output_file_path)

        else:
            src_file = str((root / file).resolve())
            target_file = str((output_path / file).resolve())
            logger.debug(
                "source file %s is not a template, copying to %s", src_file, target_file
            )
            shutil.copyfile(src_file, target_file)
            rendered_paths.append(target_file)

    return rendered_paths
