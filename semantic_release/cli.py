import click

from semantic_release.helpers import (evaluate_version_bump, get_current_version, get_new_version,
                                      set_new_version)


@click.command()
@click.argument('command')
@click.option('--force-level')
def main(command, **kwargs):
    globals()[command](**kwargs)


def version(**kwargs):
    click.echo('Creating new version..')
    current_version = get_current_version()
    click.echo('Current version: {0}'.format(current_version))
    level_bump = evaluate_version_bump(kwargs['force_level'])
    new_version = get_new_version(current_version, level_bump)
    set_new_version(new_version)
    click.echo('Bumping with a {0} version to {1}.'.format(level_bump, new_version))


if __name__ == '__main__':
    main()
