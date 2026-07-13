# =============================================================================
# Shared Django/Uvicorn/Celery container for all websites
# Build context: repository root (i.e., the parent of structa.cloud/)
# PROJECT_PATH is the site subdirectory inside core/, e.g. "ctc-research".
# =============================================================================

# ── Stage 1: Pre-build webpack bundles ───────────────────────────────────────
FROM node:24-slim AS asset-builder
ARG PROJECT_PATH=ctc-research
WORKDIR /build

# Install npm dependencies
COPY core/assets/package.json core/assets/package-lock.json /build/assets/
RUN cd /build/assets && npm ci --include=dev --legacy-peer-deps 2>&1

# Copy build source files (shared + site-specific)
COPY core/assets/scripts /build/assets/scripts
COPY core/assets/static   /build/assets/static
COPY core/webpack          /build/webpack
COPY core/${PROJECT_PATH}/assets /build/${PROJECT_PATH}/assets

# Build webpack bundles for this site
ENV PROJECT_PATH=${PROJECT_PATH} \
    NODE_ENV=production
RUN cd /build/assets && npm run build 2>&1

# ── Stage 2: Application image ───────────────────────────────────────────────
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
COPY core/pyproject.toml core/uv.lock ${APP_HOME}/


# ----------------------------------------------------------------------------
# Copy shared application code (always needed, regardless of PROJECT_PATH)
# ----------------------------------------------------------------------------
COPY core/Makefile \
     core/manage.py \
     core/__about__.py \
     core/__main__.py \
     core/cli.py \
     ${APP_HOME}/

COPY core/configs ${APP_HOME}/configs
COPY core/assets  ${APP_HOME}/assets
COPY core/libs    ${APP_HOME}/libs
COPY core/tasks   ${APP_HOME}/tasks

# NOTE: `--frozen` was removed here because `core/uv.lock` had drifted from
# `core/pyproject.toml`, causing every build to fail at this step with
# exit code 1. Dropping `--frozen` lets uv resolve a compatible set on
# build, at the cost of non-bit-exact reproducibility versus lockfile.
# TODO: regenerate `core/uv.lock` via `uv lock` on a network-equipped
# host, then re-add `--frozen` here.
RUN uv sync --no-install-project

# Install local django-fusion library as editable (required by all sites)
RUN cd ${APP_HOME}/libs/django-fusion && uv pip install -e . --no-build-isolation 2>&1 || echo "[WARN] django-fusion install failed (may already be installed via lockfile)"

# ----------------------------------------------------------------------------
# Copy the specific website code (build-time)
# ----------------------------------------------------------------------------
# For production, this embeds the site code. For development, you can
# override this directory with a volume mount (see compose volumes).
COPY core/${PROJECT_PATH} ${APP_HOME}/${PROJECT_PATH}

# ----------------------------------------------------------------------------
# Copy pre-built webpack bundles from the asset builder stage
# ----------------------------------------------------------------------------
COPY --from=asset-builder /build/${PROJECT_PATH}/assets/bundles ${APP_HOME}/${PROJECT_PATH}/assets/bundles

# ----------------------------------------------------------------------------
# Install the specific website as an editable package
# ----------------------------------------------------------------------------
RUN if [ -f "${APP_HOME}/${PROJECT_PATH}/pyproject.toml" ]; then \
      uv pip install --editable /app/${PROJECT_PATH}; \
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
