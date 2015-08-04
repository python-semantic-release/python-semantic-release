Automatic releases
------------------

The key point with using this package is to automate your releases and stop worrying about
version numbers. Different approaches to automatic releases and publishing with the help of
this package can be found below. Using a CI is the recommended approach.

Publish with CI
~~~~~~~~~~~~~~~
Add ``python setup.py publish`` as an after success task on your preferred Continuous Integration
service. Ensure that you have configured the CI so that it can upload to pypi and push to git and
it should be ready to role.

Publish with cronjobs
~~~~~~~~~~~~~~~~~~~~~

This is for you if for some reason you cannot publish from your CI or you would like releases to
drop at a certain interval. Before you start, answer this: Are you sure you do not want a CI to
release for you? (high version numbers are not a bad thing).

The guide below is for setting up scheduled publishing on a server. It requires that the user
that runs the cronjob has push access to the repository and upload access to pypi.

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
      $VENV/semantic-release publish
      cd ..
    }

    publish <package1>
    publish <package2>

4. Add cronjob::

    /bin/bash -c "cd <path> && source semantic_release/bin/activate && ./publish 2>&1 >> releases.log"
