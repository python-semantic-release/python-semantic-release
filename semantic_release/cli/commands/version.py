import click
from rich import print as rprint

from semantic_release.version import next_version


@click.command()
@click.option(
    "--print", "print_only", is_flag=True, help="Print the next version and exit"
)
# A "--commit/--no-commit" option? Or is this better with the "--dry-run" flag?
# how about push/no-push?
@click.pass_context
def version(ctx: click.Context, print_only: bool = False) -> None:
    """
    This is the magic version function that gets the next version for you
    and if you like, will write it to all the lovely files you configure.
    """
    repo = ctx.obj.repo
    parser = ctx.obj.commit_parser
    translator = ctx.obj.version_translator
    prerelease = ctx.obj.prerelease
    assets = ctx.obj.assets
    commit_message = ctx.obj.commit_message
    major_on_zero = ctx.obj.major_on_zero

    v = next_version(
        repo=repo, translator=translator, commit_parser=parser, prerelease=prerelease
    )
    # TODO: if it's already the same/released?
    print(str(v))
    if print_only:
        ctx.exit(0)

    for declaration in ctx.obj.version_declarations:
        declaration.replace(new_version=v)

    paths = [
        declaration.path.relative_to(repo.working_dir)
        for declaration in ctx.obj.version_declarations
    ]
    repo.git.add(paths)
    if assets:
        repo.git.add(assets)

    repo.git.commit(m=commit_message.format(version=v))

    repo.git.tag("-a", v.as_tag(), m=v.as_tag())

    remote_url = ctx.hvcs_client.remote_url(use_token=not ctx.obj.ignore_token_for_push)
    # Wrap in GitCommandError handling - remove token
    repo.git.push(remote_url, repo.active_branch.name)
    repo.git.push("--tags", remote_url, repo.active_branch.name)

    rprint("[green]:sparkles: Done! :sparkles:")
