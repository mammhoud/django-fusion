# =============================================================================
# Tinker (Template Customizer) Dockerfile
# Self-contained container for the Structa template customizer.
# Build context: structa.cloud/core/  (parent of tinker/)
# =============================================================================

# ── Stage 1: Webpack asset build ─────────────────────────────────────────
FROM node:24-slim AS asset-builder

WORKDIR /build

# Copy the tinker's own package.json and install deps
COPY tinker/assets/package.json tinker/assets/package-lock.json* ./tinker/assets/
RUN npm --prefix tinker/assets ci --include=dev --legacy-peer-deps

# Copy source files and build webpack bundles
COPY tinker/assets/static ./tinker/assets/static/
COPY tinker/assets/webpack.config.js ./tinker/assets/
COPY tinker/assets/postcss.config.js ./tinker/assets/
RUN npm --prefix tinker/assets run build

# ── Stage 2: Python runtime ──────────────────────────────────────────────
FROM python:3.11-slim

ARG TINKER_PORT=5073
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=settings \
    TINKER_PORT=${TINKER_PORT} \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update && apt-get install --no-install-recommends -y \
        curl libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ──────────────────────────────────────────
COPY tinker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Copy local libraries that settings.py adds to sys.path ───────────────
COPY libs /app/libs

# ── Copy the tinker source code (excluding node_modules) ─────────────
COPY tinker/__init__.py      ${APP_HOME}/tinker/
COPY tinker/__main__.py      ${APP_HOME}/tinker/
COPY tinker/settings.py      ${APP_HOME}/tinker/
COPY tinker/urls.py          ${APP_HOME}/tinker/
COPY tinker/server.py        ${APP_HOME}/tinker/
COPY tinker/site.py          ${APP_HOME}/tinker/
COPY tinker/manage.py        ${APP_HOME}/tinker/
COPY tinker/Makefile         ${APP_HOME}/tinker/
COPY tinker/chat             ${APP_HOME}/tinker/chat/
COPY tinker/templates        ${APP_HOME}/tinker/templates/
COPY tinker/docs             ${APP_HOME}/tinker/docs/
COPY tinker/assets/static    ${APP_HOME}/tinker/assets/static/

# ── Copy pre-built webpack bundles from asset-builder stage ──────────────
COPY --from=asset-builder /build/tinker/assets/bundles ${APP_HOME}/tinker/assets/bundles

# ── Create data directories ──────────────────────────────────────────────
RUN mkdir -p ${APP_HOME}/tinker/data \
             ${APP_HOME}/tinker/logs \
             ${APP_HOME}/tinker/staticfiles \
             ${APP_HOME}/tinker/assets/media \
    && chmod -R 755 ${APP_HOME}/tinker/data

# ── Collect static files (failure is non-fatal; bundles may not exist yet) ─
RUN cd ${APP_HOME}/tinker && python manage.py collectstatic --noinput --clear 2>&1 || \
    echo "  ⚠️  collectstatic had issues (non-fatal, will retry at runtime)"

# ── Healthcheck ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://127.0.0.1:${TINKER_PORT}/ || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────
COPY tinker/docker-entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

EXPOSE ${TINKER_PORT}

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
