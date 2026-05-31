# =====================================================
# Base image: Ubuntu 22.04 + Python 3.11 + Node.js + uv
# =====================================================
FROM ubuntu:22.04 AS app-base

ARG APP_HOME=/app
ARG USER_NAME=django
ARG GROUP_NAME=django

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=system \
    UV_NO_CACHE=1 \
    NODE_ENV=production \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH"

WORKDIR ${APP_HOME}

# -----------------------------------------------------
# 1️⃣ Install System Packages + Python 3.11 + Node.js + uv
# -----------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    nano \
    gettext \
    sudo \
    bash-completion \
    ca-certificates \
    ssh \
    make \
    build-essential \
    software-properties-common \
    gnupg \
    dirmngr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes PPA (requires gnupg & dirmngr)
RUN add-apt-repository -y ppa:deadsnakes/ppa

# Now install Python 3.11 and libpq-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    libpq-dev \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && npm cache clean --force

# Install pipx and then uv
RUN python3.11 -m ensurepip --upgrade \
    && python3.11 -m pip install --no-cache-dir pipx \
    && pipx install uv \
    && pipx ensurepath

# -----------------------------------------------------
# 2️⃣ Copy and install dependencies
# -----------------------------------------------------

# Copy manifests first for caching
COPY ./v1/package*.json ${APP_HOME}/
COPY ./v1/pyproject.toml ${APP_HOME}/
COPY ./v1/uv.lock ${APP_HOME}/

# -----------------------------------------------------
# 3️⃣ Application Source Code
# NOTE: Code is mounted via volumes in docker-compose for development
# For production builds without volumes, uncomment the line below:
# COPY ./ ${APP_HOME}/
# This enables live code reloading and faster iteration in development
# Volumes are configured in docker-compose.yml and docker-compose.warehouse.yml
# See: volumes: [../:/app:z, ../v1/assets/media:/a../v1/assets/media:z]
# -----------------------------------------------------

# -----------------------------------------------------
# 4️⃣ Entrypoint and Start Script
# -----------------------------------------------------
COPY ./compose/django/entrypoint /entrypoint

# Fix Windows line endings
RUN sed -i 's/\r$//g' /entrypoint /app/Makefile 2>/dev/null; \
    chmod +x /entrypoint

# -----------------------------------------------------
# 5️⃣ Default Entrypoint & Command
# -----------------------------------------------------
ENTRYPOINT ["/entrypoint"]
CMD ["server"]
