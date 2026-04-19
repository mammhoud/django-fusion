# =====================================================
# Structa — Django/Uvicorn container
# Build context: structa.cloud directory (.)
# =====================================================
FROM python:3.12-slim AS app-base

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1 \
    NODE_ENV=production \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

WORKDIR ${APP_HOME}

# -----------------------------------------------------
# 1. System packages + Node.js + uv
# -----------------------------------------------------
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl wget git nano libpq-dev gettext sudo \
    bash-completion ca-certificates ssh pipx make build-essential \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g npm@latest \
  && npm cache clean --force

RUN pipx install uv && pipx ensurepath

# -----------------------------------------------------
# 2. Create shared venv and install workspace libs
# -----------------------------------------------------
RUN uv venv /opt/venv

# Copy venv/libs packages (editable installs)
COPY ./libs /venv/libs

RUN uv pip install --python /opt/venv/bin/python \
        -e /venv/libs/django-osoul \
        -e /venv/libs/django-rseal \
        -e /venv/libs/django-grep \
        -e /venv/libs/nawaai

# -----------------------------------------------------
# 3. Install structa.cloud Python dependencies
# -----------------------------------------------------
# Copy only the dependency manifests first (better layer caching)
COPY pyproject.toml uv.lock ./

# uv sync reads pyproject.toml + uv.lock — single source of truth.
# UV_PROJECT_ENVIRONMENT points uv at our shared venv.
# --no-install-project: install deps only, not the project package itself.
# --frozen: use exact pinned versions from uv.lock.
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"
RUN uv sync \
        --frozen \
        --no-install-project

# -----------------------------------------------------
# 4. Copy application source
# -----------------------------------------------------
COPY package*.json ${APP_HOME}/
COPY . ${APP_HOME}/

# -----------------------------------------------------
# 5. Entrypoint and start scripts
# -----------------------------------------------------
RUN mkdir -p /app/logs

COPY compose/django/entrypoint /entrypoint
COPY compose/django/start /start
COPY compose/django/rqworker-start /rqworker-start

RUN sed -i 's/\r$//g' /entrypoint /start /rqworker-start \
    && chmod +x /entrypoint /start /rqworker-start

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
