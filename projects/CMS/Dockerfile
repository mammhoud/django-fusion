# =============================================================================
# Syntara – AI Chat Customizer Dockerfile
# Self-contained container for the Structa AI chat customizer.
# Build context: projects/syntara/  (self-contained)
# =============================================================================

# ── Stage 1: Webpack asset build ─────────────────────────────────────────
FROM node:24-slim AS asset-builder

WORKDIR /build

# Copy the app's own package.json and install deps
COPY assets/package.json assets/package-lock.json* ./assets/
RUN npm --prefix assets ci --include=dev --legacy-peer-deps

# Copy source files and build webpack bundles
COPY assets/static ./assets/static/
COPY assets/webpack.config.js ./assets/
COPY assets/postcss.config.js ./assets/
RUN npm --prefix assets run build

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
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ──────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# ── Copy local libraries that settings.py adds to sys.path ───────────────
COPY libs /app/libs

# ── Copy the app source code (excluding node_modules) ───────────────────
COPY __init__.py      ${APP_HOME}/syntara/
COPY __main__.py      ${APP_HOME}/syntara/
COPY settings.py      ${APP_HOME}/syntara/
COPY urls.py          ${APP_HOME}/syntara/
COPY server.py        ${APP_HOME}/syntara/
COPY site.py          ${APP_HOME}/syntara/
COPY manage.py        ${APP_HOME}/syntara/
COPY Makefile         ${APP_HOME}/syntara/
COPY chat             ${APP_HOME}/syntara/chat/
COPY templates        ${APP_HOME}/syntara/templates/
COPY docs             ${APP_HOME}/syntara/docs/
COPY assets/static    ${APP_HOME}/syntara/assets/static/

# ── Copy pre-built webpack bundles from asset-builder stage ──────────────
COPY --from=asset-builder /build/assets/bundles ${APP_HOME}/syntara/assets/bundles

# ── Create data directories ──────────────────────────────────────────────
RUN mkdir -p ${APP_HOME}/syntara/data \
             ${APP_HOME}/syntara/logs \
             ${APP_HOME}/syntara/staticfiles \
             ${APP_HOME}/syntara/assets/media \
    && chmod -R 755 ${APP_HOME}/syntara/data

# ── Collect static files (failure is non-fatal; bundles may not exist yet) ─
RUN cd ${APP_HOME}/syntara && python manage.py collectstatic --noinput --clear 2>&1 || \
    echo "  ⚠️  collectstatic had issues (non-fatal, will retry at runtime)"

# ── Healthcheck ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=15s \
    CMD curl -f http://127.0.0.1:${CYPERCLOUD_PORT}/ || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────
COPY docker-entrypoint.sh /entrypoint
RUN chmod +x /entrypoint

EXPOSE ${CYPERCLOUD_PORT}

ENTRYPOINT ["/entrypoint"]
CMD ["server"]
