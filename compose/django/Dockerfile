# =====================================================
# Structa — Django/Uvicorn container
# Build context: workspace root (parent of websites/)
# PROJECT_PATH arg is relative to websites/, e.g. "ctc-research.com"
# =====================================================
FROM python:3.12-slim AS app-base

ARG PROJECT_PATH=structa.cloud
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1 \
    NODE_ENV=production \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    UV_PROJECT_ENVIRONMENT="/opt/venv" \
    PROJECT_PATH=${PROJECT_PATH}

WORKDIR ${APP_HOME}

# -----------------------------------------------------
# 1. System packages + Node.js + uv
# -----------------------------------------------------
RUN apt-get update && apt-get install --no-install-recommends -y \
        curl wget git nano libpq-dev gettext sudo \
        bash-completion ca-certificates ssh pipx make build-essential cron \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && npm cache clean --force

RUN pipx install uv && pipx ensurepath

# -----------------------------------------------------
# 2. Create venv
# -----------------------------------------------------
RUN uv venv /opt/venv

# -----------------------------------------------------
# 3. Install dependencies from pyproject.toml
#    django-osoul, django-rseal, django-grep are pulled
#    directly from GitHub via [tool.uv.sources]
# -----------------------------------------------------
COPY websites/${PROJECT_PATH}/pyproject.toml ./pyproject.toml
COPY websites/${PROJECT_PATH}/uv.lock* ./

RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --no-install-project; \
    fi

# -----------------------------------------------------
# 3b. Patch broken django_rseal.services.communication
#     The installed package references invitation_service
#     which is missing from the distribution. Create a
#     stub so the package initialises without error.
# -----------------------------------------------------
RUN mkdir -p "/opt/venv/lib/python3.12/site-packages/django_rseal/services/communication" && \
    COMM_DIR="/opt/venv/lib/python3.12/site-packages/django_rseal/services/communication" && \
    if [ ! -f "${COMM_DIR}/invitation_service.py" ]; then \
        printf '# stub – missing from installed distribution\nclass InvitationService:\n    pass\n' \
            > "${COMM_DIR}/invitation_service.py"; \
    fi

# -----------------------------------------------------
# 4. Copy application source
# -----------------------------------------------------
COPY websites/${PROJECT_PATH}/package*.json ${APP_HOME}/
COPY websites/${PROJECT_PATH}/ ${APP_HOME}/

# Copy shared webpack config
COPY websites/webpack/ ${APP_HOME}/webpack/

# Copy shared assets (fonts, images, js, videos, static.js, shared styles)
# Webpack alias 'shared' → /app/shared/assets/static/
COPY websites/assets/static/ ${APP_HOME}/shared/assets/static/

# Copy shared configuration package so `import configs` works inside the image
COPY websites/configs/ ${APP_HOME}/configs/

# Copy shared background task project for Celery workers
COPY tasks/ ${APP_HOME}/tasks/

# Copy workspace-level multi-site manage.py so containers can select a site
# via `--site` or `DJANGO_SITE` env var. This ensures runtime switching.
COPY websites/manage.py ${APP_HOME}/manage.py

# Note: shared core package is within each website's www/ directory
# Each website has its own www/core/ package for app-specific core functionality

# -----------------------------------------------------
# 4b. Frontend assets are now mounted via volume (faster builds)
#    To build frontend assets, run locally:
#    cd websites/structa.cloud && npm install && npm run build:prod
#    Assets will be mounted from websites/structa.cloud/assets/
# -----------------------------------------------------
# Original build removed for faster container rebuilds
# Build assets are now shared via volume mounts in docker-compose

# -----------------------------------------------------
# 5. Entrypoint and start scripts
# -----------------------------------------------------
RUN mkdir -p /app/logs

COPY websites/compose/django/entrypoint /entrypoint
COPY websites/compose/django/start /start
COPY websites/compose/django/rqworker-start /rqworker-start

RUN sed -i 's/\r$//g' /entrypoint /start /rqworker-start \
    && chmod +x /entrypoint /start /rqworker-start

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
