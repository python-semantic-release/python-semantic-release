import os

import click

from semantic_release import ci_checks

from .history import (evaluate_version_bump, get_current_version, get_new_version,
                      get_previous_version, set_new_version)
from .history.logs import CHANGELOG_SECTIONS, generate_changelog, markdown_changelog
from .hvcs import check_build_status, check_token, post_changelog
from .pypi import upload_to_pypi
from .settings import config
from .vcs_helpers import (checkout, commit_new_version, get_current_head_hash,
                          get_repository_owner_and_name, push_new_version, tag_new_version)


@click.command()
@click.argument('command')
@click.option('--major', 'force_level', flag_value='major', help='Force major version.')
@click.option('--minor', 'force_level', flag_value='minor', help='Force minor version.')
@click.option('--patch', 'force_level', flag_value='patch', help='Force patch version.')
@click.option('--post', is_flag=True, help='Post changelog.')
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
        click.echo('{0} Should have bumped from {1} to {2}.'.format(
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


def changelog(**kwargs):
    """
    Generates the changelog since the last release.
    """
    current_version = get_current_version()
    log = generate_changelog(get_previous_version(current_version), current_version)
    for section in CHANGELOG_SECTIONS:
        if not log[section]:
            continue

        click.echo(section.capitalize())
        click.echo(''.join(['-' for i in range(len(section))]))
        for item in log[section]:
            click.echo(' - {0}'.format(item))
        click.echo('\n')

    if not kwargs.get('noop') and kwargs.get('post'):
        if check_token():
            owner, name = get_repository_owner_and_name()
            click.echo('Updating changelog')
            post_changelog(
                owner,
                name,
                current_version,
                markdown_changelog(current_version, log, header=False)
            )
        else:
            click.echo(click.style('Missing token: cannot post changelog', 'red'), err=True)


def publish(**kwargs):
    """
    Runs the version task before pushing to git and uploading to pypi.
    """
    current_version = get_current_version()
    click.echo('Current version: {0}'.format(current_version))
    level_bump = evaluate_version_bump(current_version, kwargs['force_level'])
    new_version = get_new_version(current_version, level_bump)
    owner, name = get_repository_owner_and_name()

    ci_checks.check('master')
    checkout('master')

    if version(**kwargs):
        push_new_version(
            gh_token=os.environ.get('GH_TOKEN'),
            owner=owner,
            name=name
        )

        if config.getboolean('semantic_release', 'upload_to_pypi'):
            upload_to_pypi(
                username=os.environ.get('PYPI_USERNAME'),
                password=os.environ.get('PYPI_PASSWORD'),
            )

        if check_token():
            click.echo('Updating changelog')
            log = generate_changelog(current_version, new_version)
            post_changelog(
                owner,
                name,
                new_version,
                markdown_changelog(new_version, log, header=False)
            )
        else:
            click.echo(click.style('Missing token: cannot post changelog', 'red'), err=True)

        click.echo(click.style('New release published', 'green'))
    else:
        click.echo('Version failed, no release will be published.', err=True)


if __name__ == '__main__':
    main()
