.. _cronjobs:

Cron Job Publishing
===================

This is for you if for some reason you cannot publish from your CI or you would like releases to
drop at a certain interval. Before you start, answer this: Are you sure you do not want a CI to
release for you? (high version numbers are not a bad thing).

The guide below is for setting up scheduled publishing on a server. It requires that the user
that runs the cronjob has push access to the repository and upload access to an artifact repository.

1. Create a virtualenv::

    virtualenv semantic_release -p `which python3`

2. Install python-semantic-release::

    pip install python-semantic-release

3. Clone the repositories you want to have scheduled publishing.
3. Put the following in ``publish``::

    VENV=semantic_release/bin

    $VENV/pip install -U pip python-semantic-release > /dev/null

    publish() {
      cd $1
      git stash -u # ensures that there is no untracked files in the directory
      git fetch && git reset --hard origin/master
      $VENV/semantic-release version && $VENV/semantic-release publish
      cd ..
    }

    publish <package1>
    publish <package2>

4. Add cronjob::

    /bin/bash -c "cd <path> && source semantic_release/bin/activate && ./publish 2>&1 >> releases.log"
