import click

from semantic_release.git_helpers import commit_new_version, tag_new_version
from semantic_release.helpers import get_current_version, get_new_version, set_new_version
from semantic_release.history import evaluate_version_bump


@click.command()
@click.argument('command')
@click.option('--major', 'force_level', flag_value='major', help='Force major version.')
@click.option('--minor', 'force_level', flag_value='minor', help='Force minor version.')
@click.option('--patch', 'force_level', flag_value='patch', help='Force patch version.')
@click.option('--noop', is_flag=True,
              help='No-operations mode, finds the new version number without changing it.')
def main(command, **kwargs):
    """
    Routes to the correct cli function. Looks up the command
    in the global scope and calls the function.
    :param command: String with the name of the function to call
    :param kwargs: All click options.
    """
    globals()[command](**kwargs)


def version(**kwargs):
    """
    Detects the new version according to git log and semver. Writes the new version
    number and commits it(unless the noop-option is True.
    """
    click.echo('Creating new version..')
    current_version = get_current_version()
    click.echo('Current version: {0}'.format(current_version))
    level_bump = evaluate_version_bump(current_version, kwargs['force_level'])
    new_version = get_new_version(current_version, level_bump)

    if new_version == current_version:
        click.echo(click.style('No release will be made.', fg='yellow'))
        return

    if kwargs['noop'] is True:
        click.echo('{} Should have bumped from {} to {}.'.format(
            click.style('No operation mode.', fg='yellow'),
            current_version,
            new_version
        ))
        return

    set_new_version(new_version)
    commit_new_version(new_version)
    tag_new_version(new_version)
    click.echo('Bumping with a {0} version to {1}.'.format(level_bump, new_version))


if __name__ == '__main__':
    main()
