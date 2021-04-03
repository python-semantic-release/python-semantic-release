# This Dockerfile is only for GitHub Actions
FROM python:3.7

ENV PYTHONPATH /semantic-release

COPY . /semantic-release

RUN cd /semantic-release && \
    python -m venv /semantic-release/.venv && \
    /semantic-release/.venv/bin/pip install .

RUN /semantic-release/.venv/bin/python -m semantic_release.cli --help

ENTRYPOINT ["/semantic-release/action.sh"]
