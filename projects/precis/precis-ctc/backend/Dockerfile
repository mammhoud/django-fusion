# =============================================================================
# Backend container for precis-ctc (CTC Research)
# Build context: project root (projects/precis/precis-ctc)
# Shared workspace dependencies arrive as additional build contexts:
#   - workspace  → repository root (projects/, libs/, tests/)
#   - configs    → projects/precis/configs (shared Django settings package)
# This keeps the build scoped to this project's files instead of shipping the
# whole monorepo into the image.
# =============================================================================

FROM python:3.11-slim

ARG PROJECT_PATH=precis-ctc
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    NODE_ENV=production \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    VIRTUAL_ENV="/opt/venv" \
    UV_PROJECT_ENVIRONMENT="/opt/venv" \
    PROJECT_PATH=${PROJECT_PATH} \
    DJANGO_SITE=${PROJECT_PATH} \
    WEBSITE=${PROJECT_PATH} \
    APP_MODULE=server:application \
    APP_HOME=${APP_HOME}

WORKDIR ${APP_HOME}

# ── System packages + Node.js + uv ──────────────────────────────────────────
RUN apt-get update && apt-get install --no-install-recommends -y \
        bash-completion build-essential ca-certificates cron curl gettext git \
        libpq-dev make nano ssh sudo wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install --no-install-recommends -y nodejs \
    && npm install -g npm@latest \
    && npm cache clean --force \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools uv \
    && uv venv /opt/venv \
    && uv pip install --python /opt/venv/bin/python setuptools

# ── Python dependencies (workspace additional context) ─────────────────────
COPY --from=workspace /projects/pyproject.toml /projects/uv.lock ${APP_HOME}/
COPY --from=workspace /projects/Makefile \
     /projects/manage.py \
     /projects/__about__.py \
     /projects/__main__.py \
     /projects/cli.py \
     ${APP_HOME}/

# ── Shared libraries (workspace additional context) ────────────────────────
COPY --from=workspace /libs ${APP_HOME}/libs

# Symlink so uv resolves "../libs/django-fusion" from pyproject.toml
RUN ln -sf ${APP_HOME}/libs /libs

RUN uv sync --no-install-project

RUN uv pip install --python /opt/venv/bin/python setuptools wheel \
    && cd ${APP_HOME}/libs/django-fusion \
    && uv pip install -e . --no-build-isolation

# ── Project-specific backend code (project build context) ──────────────────
# The runtime site root is the backend root. This matches the bind mount in
# Compose and keeps manage.py, the settings/ package, assets, and module
# imports on one canonical path in both image-only and development-container
# runs.
COPY backend ${APP_HOME}/${PROJECT_PATH}
# Canonical shared settings package (configs additional context).
COPY --from=configs / ${APP_HOME}/${PROJECT_PATH}/configs
COPY Env ${APP_HOME}/${PROJECT_PATH}/Env
# Project-level config cascade (configs/*.yml — defaults/site/admin). In this
# image the site root's configs/ dir also hosts the shared settings package
# (COPIED above), so the YAMLs land at its top level — exactly the
# `<SITE_DIR>/configs/*.yml` glob conf.py loads before Env/_site.yml.
COPY configs ${APP_HOME}/${PROJECT_PATH}/configs
# Asset/template source is part of the runtime image. Production Compose does
# not bind-mount source directories because remote Docker engines can expose a
# partial synchronized tree and mask the files copied above.
COPY assets ${APP_HOME}/assets
# Runtime setup and optional fixture verification use the shared workspace
# utilities; keep them available in image-only deployments as well.
COPY --from=workspace /tests ${APP_HOME}/tests

# Install the backend package from the migrated project layout.
RUN if [ -f "${APP_HOME}/${PROJECT_PATH}/pyproject.toml" ]; then \
      uv pip install --editable /app/${PROJECT_PATH}; \
    fi

# ── Entrypoint and helper scripts ───────────────────────────────────────────
COPY backend/prepare /prepare
# The server helper lives inside the site dir (container /run is a system dir),
# so the entrypoint can dispatch `server` directly to it.
COPY backend/run    ${APP_HOME}/${PROJECT_PATH}/run
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/media ${APP_HOME}/${PROJECT_PATH}/assets/staticfiles \
    && sed -i 's/\r$//g' /prepare ${APP_HOME}/${PROJECT_PATH}/run \
    && chmod +x /prepare ${APP_HOME}/${PROJECT_PATH}/run

ENTRYPOINT ["/prepare"]
CMD ["server"]
