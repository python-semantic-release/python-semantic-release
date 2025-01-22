# This Dockerfile is only for GitHub Actions
FROM python:3.13-bookworm

# Copy python-semantic-release source code into container
COPY . /psr

RUN \
    # Install desired packages
    apt update && apt install -y --no-install-recommends \
        # install git with git-lfs support
        git git-lfs \
        # install python cmodule / binary module build utilities
        python3-dev gcc make cmake cargo \
    # Configure global pip
    && { \
        printf '%s\n' "[global]"; \
        printf '%s\n' "no-cache-dir = true"; \
        printf '%s\n' "disable-pip-version-check = true"; \
    } > /etc/pip.conf \
    # Create virtual environment for python-semantic-release
    && python3 -m venv /psr/.venv \
    # Update core utilities in the virtual environment
    && /psr/.venv/bin/pip install -U pip setuptools wheel \
    # Install psr & its dependencies from source into virtual environment
    && /psr/.venv/bin/pip install /psr \
    # Cleanup
    && apt clean -y

ENV PSR_DOCKER_GITHUB_ACTION=true

ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["/bin/bash", "-l", "/psr/action.sh"]
