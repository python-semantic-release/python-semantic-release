# This Dockerfile is only for GitHub Actions
FROM python:3.9

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        git-lfs

ENV PYTHONPATH /semantic-release

COPY . /semantic-release

RUN cd /semantic-release && \
    python -m venv /semantic-release/.venv && \
    /semantic-release/.venv/bin/pip install .

RUN /semantic-release/.venv/bin/python -m semantic_release.cli --help

ENTRYPOINT ["/semantic-release/action.sh"]
