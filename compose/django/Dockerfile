# =====================================================
# Shared Django/Uvicorn/Celery container
# Build context: repository root
# PROJECT_PATH is a site directory, e.g. "ctc-research" or "lms-demo".
# =====================================================
FROM python:3.12-slim AS app-base

ARG PROJECT_PATH=ctc-research
ARG APP_HOME=/app
ARG USER_NAME=django
ARG GROUP_NAME=django

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
    APP_HOME=${APP_HOME}

WORKDIR ${APP_HOME}

# -----------------------------------------------------
# System packages + Node.js + uv
# -----------------------------------------------------
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

# -----------------------------------------------------
# Install Python dependencies from the single root manifest
# -----------------------------------------------------
COPY pyproject.toml uv.lock* ${APP_HOME}/

RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --no-install-project; \
    fi

# -----------------------------------------------------
# Copy shared source and the selected website
# -----------------------------------------------------
COPY Makefile manage.py __about__.py __main__.py cli.py ${APP_HOME}/
COPY configs ${APP_HOME}/configs
COPY assets ${APP_HOME}/assets
COPY compose ${APP_HOME}/compose
COPY tests ${APP_HOME}/tests
COPY tasks ${APP_HOME}/tasks
COPY ${PROJECT_PATH} ${APP_HOME}/${PROJECT_PATH}

# -----------------------------------------------------
# Install the shared frontend toolchain in the image.
# -----------------------------------------------------
# Build/collect commands may run at container startup, so install dev tooling
# explicitly even though NODE_ENV defaults to production. This keeps webpack-cli
# available non-interactively and avoids npx install prompts.
RUN cd ${APP_HOME}/assets \
    && npm ci --include=dev --legacy-peer-deps --no-audit --no-fund

# -----------------------------------------------------
# Entrypoint and helper scripts
# -----------------------------------------------------
RUN mkdir -p ${APP_HOME}/logs \
    && sed -i 's/\r$//g' /app/compose/django/entrypoint /app/compose/django/start /app/compose/django/rqworker-start /app/compose/django/flower /app/Makefile \
    && cp /app/compose/django/entrypoint /entrypoint \
    && cp /app/compose/django/start /start \
    && cp /app/compose/django/rqworker-start /rqworker-start \
    && cp /app/compose/django/flower /flower \
    && chmod +x /entrypoint /start /rqworker-start /flower

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
