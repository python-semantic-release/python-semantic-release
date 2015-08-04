import click

from .history import evaluate_version_bump, get_current_version, get_new_version, set_new_version
from .hvcs import check_build_status
from .pypi import upload_to_pypi
from .settings import config
from .vcs_helpers import (commit_new_version, get_current_head_hash, get_repository_owner_and_name,
                          push_new_version, tag_new_version)


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
        return False

    if kwargs['noop'] is True:
        click.echo('{} Should have bumped from {} to {}.'.format(
            click.style('No operation mode.', fg='yellow'),
            current_version,
            new_version
        ))
        return False

    if config.getboolean('semantic_release', 'check_build_status'):
        click.echo('Checking build status..')
        owner, name = get_repository_owner_and_name()
        if not check_build_status(owner, name, get_current_head_hash()):
            click.echo(click.style('The build has failed', 'red'))
            return False
        click.echo(click.style('The build was a success, continuing the release', 'green'))

    set_new_version(new_version)
    commit_new_version(new_version)
    tag_new_version(new_version)
    click.echo('Bumping with a {0} version to {1}.'.format(level_bump, new_version))
    return True


def publish(**kwargs):
    """
    Runs the version task before pushing to git and uploading to pypi.
    """
    if version(**kwargs):
        push_new_version()
        upload_to_pypi()
        click.echo(click.style('New release published', 'green'))
    else:
        click.echo('Version failed, no release will be published.')


if __name__ == '__main__':
    main()
