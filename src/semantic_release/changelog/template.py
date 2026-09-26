from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from jinja2 import BaseLoader, TemplateNotFound
from jinja2.sandbox import SandboxedEnvironment
from upath import UPath

from semantic_release.globals import logger
from semantic_release.helpers import dynamic_import

if TYPE_CHECKING:  # pragma: no cover
    import os
    from typing import Callable, Iterable, Literal

    from jinja2 import Environment


class UPathLoader(BaseLoader):
    """
    Jinja2 loader using UPath for universal filesystem abstraction.

    This loader enables loading templates from any filesystem supported by fsspec/UPath,
    including local files, git repositories, HTTP URLs, S3 buckets, etc.
    """

    def __init__(
        self,
        searchpath: UPath,
        encoding: str = "utf-8",
    ) -> None:
        self.searchpath = searchpath
        self.encoding = encoding

    def get_source(
        self, _environment: Environment, template: str
    ) -> tuple[str, str, Callable[[], bool]]:
        path = self.searchpath / template
        if not path.exists():
            raise TemplateNotFound(template)
        source = path.read_text(encoding=self.encoding)
        return source, str(path), lambda: True

    def list_templates(self) -> list[str]:
        templates: list[str] = []
        for f in self.searchpath.rglob("*"):
            if f.is_file():
                rel_path = PurePosixPath(f.path).relative_to(self.searchpath.path)
                templates.append(str(rel_path))
        return templates


# pylint: disable=too-many-arguments,too-many-locals
def environment(
    template_dir: Path | UPath | str = ".",
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
    Create a jinja2.sandbox.SandboxedEnvironment with certain parameter restrictions.

    Uses UPathLoader which supports both local and remote template directories
    (git repositories, HTTP URLs, S3 buckets, etc.) via fsspec/UPath.

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

    if not isinstance(template_dir, UPath):
        template_dir = UPath(template_dir)

    loader = UPathLoader(template_dir, encoding="utf-8")

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
        loader=loader,
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
    template_dir: Path | UPath | str,
    environment: Environment,
    _root_dir: str | os.PathLike[str] = ".",
) -> list[str]:
    rendered_paths: list[str] = []
    root_dir = Path(_root_dir)

    if not isinstance(template_dir, UPath):
        template_dir = UPath(template_dir)

    for src_file in template_dir.rglob("*"):
        if not src_file.is_file():
            continue

        # Convert to PurePosixPath for local path operations.
        # PurePosixPath is correct because remote filesystems always use forward slashes
        rel_path = PurePosixPath(src_file.path).relative_to(template_dir.path)

        if any(part.startswith(".") for part in rel_path.parts):
            continue

        output_path = (root_dir / rel_path.parent).resolve()
        logger.info("Rendering templates from %s to %s", src_file.parent, output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        if rel_path.suffix == ".j2":
            src_file_rel = str(rel_path)
            output_file_path = output_path / rel_path.stem

            # Although, file stream rendering is possible and preferred in most
            # situations, here it is not desired as you cannot read the previous
            # contents of a file during the rendering of the template. This mechanism
            # is used for inserting into a current changelog. When using stream rendering
            # of the same file, it always came back empty
            logger.debug("rendering %s to %s", src_file_rel, output_file_path)
            rendered_file = environment.get_template(src_file_rel).render().rstrip()
            output_file_path.write_text(f"{rendered_file}\n", encoding="utf-8")

            rendered_paths.append(str(output_file_path))

        else:
            # Copy non-template file
            target_file = output_path / rel_path.name
            logger.debug("copying %s to %s", src_file, target_file)
            target_file.write_bytes(src_file.read_bytes())
            rendered_paths.append(str(target_file))

    return rendered_paths
