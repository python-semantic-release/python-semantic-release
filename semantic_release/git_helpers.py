from git import Repo
from invoke import run

from semantic_release.settings import load_config


def get_commit_log():
    repo = Repo('.git')
    for commit in repo.iter_commits():
        yield commit.message


def commit_new_version(version):
    add = run('git add {}'.format(load_config().get('version_variable').split(':')[0]), hide=True)
    if add.ok:
        run('git commit -m "{}"'.format(version), hide=True)


def tag_new_version(version):
    return run('git tag v{} HEAD'.format(version), hide=True)


def push_new_version():
    return run('git push && git push --tags', hide=True)
