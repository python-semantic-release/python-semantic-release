# This Dockerfile is only for GitHub Actions
FROM python:3.7

env PYTHONPATH /semantic-release

COPY . /semantic-release

RUN cd /semantic-release && pip install -r requirements/base.txt ; cd -

RUN python -m semantic_release.cli --help


ENTRYPOINT ["/semantic-release/action.sh"]
