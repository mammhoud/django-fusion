# =============================================================================
# Shared Django/Uvicorn/Celery container for all websites
# Build context: repository root (i.e., the parent of structa.cloud/)
# PROJECT_PATH is the site subdirectory inside applications/, e.g. "ctc-research".
# =============================================================================
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
COPY applications/pyproject.toml applications/uv.lock* ${APP_HOME}/

RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --no-install-project; \
    fi

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

# ----------------------------------------------------------------------------
# Copy the specific website code (build-time)
# ----------------------------------------------------------------------------
# For production, this embeds the site code. For development, you can
# override this directory with a volume mount (see compose volumes).
COPY applications/${PROJECT_PATH} ${APP_HOME}/${PROJECT_PATH}

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
