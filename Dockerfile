# This Dockerfile is only for GitHub Actions
FROM python:3.7

ENV PYTHONPATH /semantic-release

COPY . /semantic-release

RUN cd /semantic-release && pip install .

RUN python -m semantic_release.cli --help

ENTRYPOINT ["/semantic-release/action.sh"]
