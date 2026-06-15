# ============================================================
# Documentation Service Dockerfile (MkDocs)
# ============================================================
FROM python:3.12-slim

WORKDIR /docs

# Install MkDocs with Material theme
RUN pip install --no-cache-dir \
    mkdocs-material \
    mkdocs-mermaid2-plugin \
    mkdocs-git-revision-date-localized-plugin \
    mkdocs-minify-plugin \
    mkdocs-redirects

# Expose port
EXPOSE 8000

# Start MkDocs server
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"]
