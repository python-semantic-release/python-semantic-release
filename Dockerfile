# This Dockerfile is only for GitHub Actions
FROM python:3.10-bullseye

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    git-lfs

# install backported stable version of git, which supports ssh signing
RUN echo "deb http://deb.debian.org/debian bullseye-backports main" >> /etc/apt/sources.list; \
    apt-get update;\
    apt-get install -y git/bullseye-backports

ENV PYTHONPATH /semantic-release

COPY . /semantic-release

RUN cd /semantic-release && \
    python -m venv /semantic-release/.venv && \
    /semantic-release/.venv/bin/pip install .

RUN /semantic-release/.venv/bin/python -m semantic_release --help

ENTRYPOINT ["/semantic-release/action.sh"]
