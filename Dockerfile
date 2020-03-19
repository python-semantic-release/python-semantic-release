# This Dockerfile is only for GitHub Actions

FROM python:3.7

COPY . /python-semantic-release
RUN python -m pip install /python-semantic-release

COPY action.sh /action.sh
ENTRYPOINT ["/action.sh"]
