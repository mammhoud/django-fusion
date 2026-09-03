# =============================================================================
# Cypercloud – AI Chat Customizer Dockerfile
# Self-contained container for the Structa AI chat customizer.
# Build context: structa.cloud/projects/  (parent of cypercloud/)
# =============================================================================

# ── Stage 1: Webpack asset build ─────────────────────────────────────────
FROM node:24-slim AS asset-builder

WORKDIR /build

# Copy the cypercloud's own package.json and install deps
COPY cypercloud/assets/package.json cypercloud/assets/package-lock.json* ./cypercloud/assets/
RUN npm --prefix cypercloud/assets ci --include=dev --legacy-peer-deps

# Copy source files and build webpack bundles
COPY cypercloud/assets/static ./cypercloud/assets/static/
COPY cypercloud/assets/webpack.config.js ./cypercloud/assets/
COPY cypercloud/assets/postcss.config.js ./cypercloud/assets/
RUN npm --prefix cypercloud/assets run build

# ── Stage 2: Python runtime ──────────────────────────────────────────────
FROM python:3.11-slim

ARG CYPERCLOUD_PORT=5073
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=settings \
    CYPERCLOUD_PORT=${CYPERCLOUD_PORT} \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update && apt-get install --no-install-recommends -y \
        curl libpq-dev \
        zsh fonts-powerline graphviz \
    && rm -rf /var/lib/apt/lists/* \
    && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended \
    && sed -i 's/^ZSH_THEME=.*/ZSH_THEME="af-magic"/' /root/.zshrc \
    && echo 'plugins=(git python pip django)' >> /root/.zshrc

# ── Install Python dependencies ──────────────────────────────────────────
COPY cypercloud/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Copy local libraries that settings.py adds to sys.path ───────────────
COPY libs /app/libs

# ── Copy the cypercloud source code (excluding node_modules) ─────────────
COPY cypercloud/__init__.py      ${APP_HOME}/cypercloud/
COPY cypercloud/__main__.py      ${APP_HOME}/cypercloud/
COPY cypercloud/settings.py      ${APP_HOME}/cypercloud/
COPY cypercloud/urls.py          ${APP_HOME}/cypercloud/
COPY cypercloud/server.py        ${APP_HOME}/cypercloud/
COPY cypercloud/site.py          ${APP_HOME}/cypercloud/
COPY cypercloud/manage.py        ${APP_HOME}/cypercloud/
COPY cypercloud/Makefile         ${APP_HOME}/cypercloud/
COPY cypercloud/chat             ${APP_HOME}/cypercloud/chat/
COPY cypercloud/templates        ${APP_HOME}/cypercloud/templates/
COPY cypercloud/docs             ${APP_HOME}/cypercloud/docs/
COPY cypercloud/assets/static    ${APP_HOME}/cypercloud/assets/static/

# ── Copy pre-built webpack bundles from asset-builder stage ──────────────
COPY --from=asset-builder /build/cypercloud/assets/bundles ${APP_HOME}/cypercloud/assets/bundles

# ── Create data directories ──────────────────────────────────────────────
RUN mkdir -p ${APP_HOME}/cypercloud/data \
             ${APP_HOME}/cypercloud/logs \
             ${APP_HOME}/cypercloud/staticfiles \
             ${APP_HOME}/cypercloud/assets/media \
    && chmod -R 755 ${APP_HOME}/cypercloud/data

# ── Collect static files (failure is non-fatal; bundles may not exist yet) ─
RUN cd ${APP_HOME}/cypercloud && python manage.py collectstatic --noinput --clear 2>&1 || \
    echo "  ⚠️  collectstatic had issues (non-fatal, will retry at runtime)"

# ── Healthcheck ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://127.0.0.1:${CYPERCLOUD_PORT}/ || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────
COPY cypercloud/docker-entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

EXPOSE ${CYPERCLOUD_PORT}

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
