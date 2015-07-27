from invoke import run
import semver


def get_current_version():
    return run('python setup.py --version', hide=True).stdout.strip()


def evaluate_version_bump(force=None):
    if force:
        return force
    return 'patch'


def get_new_version(current_version, level_bump):
    return getattr(semver, 'bump_{0}'.format(level_bump))(current_version)


def set_new_version(current_version):
    return True
