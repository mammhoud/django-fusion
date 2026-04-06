# =====================================================
# Base image: Debian Bookworm + Python + Node + uv
# =====================================================
FROM python:3.12-slim AS app-base

ARG APP_HOME=/app
ARG USER_NAME=django
ARG GROUP_NAME=django

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_NO_CACHE=1 \
    NODE_ENV=production

WORKDIR ${APP_HOME}

# -----------------------------------------------------
# 1️⃣ Install System Packages + Node.js + uv
# -----------------------------------------------------
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    wget \
    git \
    nano \
    libpq-dev \
    gettext \
    sudo \
    bash-completion \
    ca-certificates \
    ssh \
    pipx \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g npm@latest \
  && npm cache clean --force


# Install uv (Python dependency manager)
RUN pipx install uv && pipx ensurepath

# -----------------------------------------------------
# 2️⃣ Copy and install dependencies
# -----------------------------------------------------

# Copy manifests first for caching
COPY package*.json ${APP_HOME}/
COPY pyproject.toml uv.lock ${APP_HOME}/

# -----------------------------------------------------
# 3️⃣ Copy application source
# -----------------------------------------------------
COPY . ${APP_HOME}/

# -----------------------------------------------------
# 4️⃣ Entrypoint and Start Script
# -----------------------------------------------------
COPY ./compose/django/entrypoint /entrypoint
COPY ./compose/django/start /start
# COPY ./compose/django/rqworker-start /rqworker-start

RUN sed -i 's/\r$//g' /entrypoint /start \
    && chmod +x /entrypoint /start
    #/rqworker-start \

# -----------------------------------------------------
# 5️⃣ Create non-root user
# -----------------------------------------------------
# RUN groupadd -r ${GROUP_NAME} && useradd -r -g ${GROUP_NAME} ${USER_NAME} \
#     && chown -R ${USER_NAME}:${GROUP_NAME} ${APP_HOME}

# USER ${USER_NAME}

# -----------------------------------------------------
# 6️⃣ Default Entrypoint
# -----------------------------------------------------
ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
