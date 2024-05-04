# This Dockerfile is only for GitHub Actions
FROM python:3.10-bullseye

# Copy python-semantic-release source code into container
COPY . /psr

RUN \
    # add backports repository
    echo "deb http://deb.debian.org/debian bullseye-backports main" >> /etc/apt/sources.list \
    # Install desired packages
    && apt update && apt install -y --no-install-recommends \
        # install git-lfs support
        git-lfs \
        # install git that supports ssh signing
        git/bullseye-backports \
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

ENTRYPOINT ["/bin/bash", "-l", "/psr/action.sh"]
