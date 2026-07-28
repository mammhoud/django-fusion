# =============================================================================
# Shared Django/Uvicorn/Celery container for all websites
# Build context: repository root (i.e., the parent of structa.cloud/)
# PROJECT_PATH is the site subdirectory inside applications/, e.g. "ctc-research".
# =============================================================================

# ── Application image ───────────────────────────────────────────────────────
FROM python:3.11-slim AS app-base

ARG PROJECT_PATH=ctc-research
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    NODE_ENV=production \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    UV_PROJECT_ENVIRONMENT="/opt/venv" \
    PROJECT_PATH=${PROJECT_PATH} \
    DJANGO_SITE=${PROJECT_PATH} \
    WEBSITE=${PROJECT_PATH} \
    APP_MODULE=server:application \
    APP_HOME=${APP_HOME}

WORKDIR ${APP_HOME}

# ----------------------------------------------------------------------------
# System packages + Node.js + uv
# ----------------------------------------------------------------------------
RUN apt-get update && apt-get install --no-install-recommends -y \
        bash-completion build-essential ca-certificates cron curl gettext git \
        libpq-dev make nano ssh sudo wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install --no-install-recommends -y nodejs \
    && npm install -g npm@latest \
    && npm cache clean --force \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip uv \
    && uv venv /opt/venv

# ----------------------------------------------------------------------------
# Install Python dependencies from the shared root manifest
# ----------------------------------------------------------------------------
COPY applications/pyproject.toml applications/uv.lock ${APP_HOME}/


# ----------------------------------------------------------------------------
# Copy shared application code (always needed, regardless of PROJECT_PATH)
# ----------------------------------------------------------------------------
COPY applications/Makefile \
     applications/manage.py \
     applications/__about__.py \
     applications/__main__.py \
     applications/cli.py \
     ${APP_HOME}/

COPY applications/configs ${APP_HOME}/configs
COPY applications/assets  ${APP_HOME}/assets
COPY applications/libs    ${APP_HOME}/libs
COPY applications/tasks   ${APP_HOME}/tasks

# Copy the shared applications package (__init__.py + www subpackage)
# needed for import paths like applications.www.core.apps.CoreConfig
COPY applications/__init__.py ${APP_HOME}/applications/__init__.py
COPY applications/www         ${APP_HOME}/applications/www

RUN uv sync --frozen --no-install-project

# Install local django-fusion library as editable (required by all sites)
RUN cd ${APP_HOME}/libs/django-fusion && uv pip install -e . 2>&1

# ----------------------------------------------------------------------------
# Copy the specific website code (build-time)
# ----------------------------------------------------------------------------
# For production, this embeds the site code. For development, you can
# override this directory with a volume mount (see compose volumes).
COPY applications/${PROJECT_PATH} ${APP_HOME}/${PROJECT_PATH}

# Note: webpack bundles are included in the general site COPY above
# (applications/${PROJECT_PATH}/assets/bundles is part of the site directory)
# The asset-builder stage was removed because node:24-slim lacks Python

# ----------------------------------------------------------------------------
# Install the specific website as an editable package
# (install hatchling first — some site pyproject.toml files use it as build backend)
# ----------------------------------------------------------------------------
RUN if [ -f "${APP_HOME}/${PROJECT_PATH}/pyproject.toml" ]; then \
      echo "[INFO] Skipping editable install — PYTHONPATH handles imports"; \
    fi

# ----------------------------------------------------------------------------
# Copy entrypoint and helper scripts (located at compose/ inside repository)
# ----------------------------------------------------------------------------
COPY compose/entrypoint     /entrypoint
COPY compose/start          /start
COPY compose/rqworker-start /rqworker-start
COPY compose/flower         /flower

RUN mkdir -p ${APP_HOME}/logs \
    && sed -i 's/\r$//g' /entrypoint /start /rqworker-start /flower \
    && chmod +x /entrypoint /start /rqworker-start /flower

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
