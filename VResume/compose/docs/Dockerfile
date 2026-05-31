# ============================================================
# VResume Documentation Service (MkDocs)
# ============================================================
# Lightweight documentation server using MkDocs Material theme
# Serves documentation with auto-reload during development
# and production-ready static output

FROM python:3.12-slim

ARG APP_HOME=/docs
ARG USER_NAME=docs
ARG GROUP_NAME=docs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR ${APP_HOME}

# ============================================================
# Install System Dependencies
# ============================================================
RUN apt-get update && apt-get install --no-install-recommends -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Create non-root user for security
# ============================================================
RUN groupadd -r ${GROUP_NAME} && useradd -r -g ${GROUP_NAME} ${USER_NAME}

# ============================================================
# Install Python dependencies
# ============================================================
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    mkdocs==1.5.3 \
    mkdocs-material==9.4.14 \
    mkdocs-include-markdown-plugin==6.1.1 \
    mkdocs-mermaid2-plugin==0.6.0 \
    pymdown-extensions==10.4 \
    python-markdown-math==0.8

# ============================================================
# Copy documentation files
# ============================================================
COPY docs/ ${APP_HOME}/docs/
COPY mkdocs.yml ${APP_HOME}/
COPY README.md ${APP_HOME}/

# ============================================================
# Build static site
# ============================================================
RUN mkdocs build -d /docs/site

# ============================================================
# Switch to non-root user
# ============================================================
USER ${USER_NAME}

# ============================================================
# Expose port and set entry command
# ============================================================
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default: serve documentation
CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
