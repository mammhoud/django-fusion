# =============================================================================
# Customizer Dockerfile
# Self-contained container for the Structa template customizer.
# Build context: structa.cloud/applications/  (parent of customizer/)
# =============================================================================

# ── Stage 1: Webpack asset build ─────────────────────────────────────────
FROM node:24-slim AS asset-builder

WORKDIR /build

# Copy the customizer's own package.json and install deps
COPY customizer/assets/package.json customizer/assets/package-lock.json* ./customizer/assets/
RUN npm --prefix customizer/assets ci --include=dev --legacy-peer-deps

# Copy source files and build webpack bundles
COPY customizer/assets/static ./customizer/assets/static/
COPY customizer/assets/webpack.config.js ./customizer/assets/
COPY customizer/assets/postcss.config.js ./customizer/assets/
RUN npm --prefix customizer/assets run build

# ── Stage 2: Python runtime ──────────────────────────────────────────────
FROM python:3.11-slim

ARG CUSTOMIZER_PORT=5073
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DJANGO_SETTINGS_MODULE=settings \
    CUSTOMIZER_PORT=${CUSTOMIZER_PORT} \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update && apt-get install --no-install-recommends -y \
        curl libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ──────────────────────────────────────────
COPY customizer/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Copy local libraries that settings.py adds to sys.path ───────────────
COPY libs /app/libs

# ── Copy the customizer source code (excluding node_modules) ─────────────
COPY customizer/__init__.py      ${APP_HOME}/customizer/
COPY customizer/__main__.py      ${APP_HOME}/customizer/
COPY customizer/settings.py      ${APP_HOME}/customizer/
COPY customizer/urls.py          ${APP_HOME}/customizer/
COPY customizer/server.py        ${APP_HOME}/customizer/
COPY customizer/site.py          ${APP_HOME}/customizer/
COPY customizer/manage.py        ${APP_HOME}/customizer/
COPY customizer/Makefile         ${APP_HOME}/customizer/
COPY customizer/chat             ${APP_HOME}/customizer/chat/
COPY customizer/templates        ${APP_HOME}/customizer/templates/
COPY customizer/docs             ${APP_HOME}/customizer/docs/
COPY customizer/assets/static    ${APP_HOME}/customizer/assets/static/

# ── Copy pre-built webpack bundles from asset-builder stage ──────────────
COPY --from=asset-builder /build/customizer/assets/bundles ${APP_HOME}/customizer/assets/bundles

# ── Create data directories ──────────────────────────────────────────────
RUN mkdir -p ${APP_HOME}/customizer/data \
             ${APP_HOME}/customizer/logs \
             ${APP_HOME}/customizer/staticfiles \
             ${APP_HOME}/customizer/assets/media \
    && chmod -R 755 ${APP_HOME}/customizer/data

# ── Collect static files (failure is non-fatal; bundles may not exist yet) ─
RUN cd ${APP_HOME}/customizer && python manage.py collectstatic --noinput --clear 2>&1 || \
    echo "  ⚠️  collectstatic had issues (non-fatal, will retry at runtime)"

# ── Healthcheck ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://127.0.0.1:${CUSTOMIZER_PORT}/ || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────
COPY customizer/docker-entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

EXPOSE ${CUSTOMIZER_PORT}

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
