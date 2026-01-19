# This Dockerfile is only for GitHub Actions
FROM python:3.14-slim-trixie
ARG WORK_DIR="/opt/psr"

WORKDIR ${WORK_DIR}

ENV PSR_DOCKER_GITHUB_ACTION=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PSR_VENV_BIN="${WORK_DIR}/.venv/bin"

# Copy action utilities into container
COPY . ./

RUN \
    # Install desired packages
    apt update && apt install -y --no-install-recommends \
        # install git with git-lfs support
        git git-lfs \
        # install ssh client for git signing
        openssh-client \
        # install python cmodule / binary module build utilities
        python3-dev gcc make cmake cargo \
    # Configure global pip
    && { \
        printf '%s\n' "[global]"; \
        printf '%s\n' "disable-pip-version-check = true"; \
    } > /etc/pip.conf \
    # Create virtual environment for python-semantic-release
    && python3 -m venv "$(dirname "${PSR_VENV_BIN}")" \
    # Update core utilities in the virtual environment
    && "${PSR_VENV_BIN}/pip" install --upgrade pip setuptools wheel \
    # Install psr & its dependencies from source into virtual environment
    && "${PSR_VENV_BIN}/pip" install --pre -r requirements.txt \
    # Validate binary availability
    && bash -c "${PSR_VENV_BIN}/semantic-release --help" \
    # make action script executable
    && chmod +x "${WORK_DIR}/action.sh" \
    # Put action script in PATH
    && ln -s "${WORK_DIR}/action.sh" /usr/local/bin/action-entrypoint \
    # Clean up
    && apt clean && rm -rf /var/lib/apt/lists/* \
    && find /tmp -mindepth 1 -delete

ENTRYPOINT ["/usr/local/bin/action-entrypoint"]
