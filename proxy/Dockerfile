FROM docker.io/traefik:latest

# Install apache2-utils for htpasswd
RUN apk add --no-cache apache2-utils

# Create ACME directory with proper permissions
RUN mkdir -p /etc/traefik/acme \
    && touch /etc/traefik/certs/acme.json \
    && chmod 600 /etc/traefik/certs/acme.json

# Ensure ownership is writable by a non-root Traefik process if necessary
RUN chown -R 1000:1000 /etc/traefik/acme || true

# Copy static configuration (dynamic dir is volume-mounted at runtime)
COPY ./traefik.yml /etc/traefik/traefik.yml
COPY ./dynamic /etc/traefik/dynamic

# Health check — Traefik 3.x uses /ping endpoint
HEALTHCHECK --interval=60s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ping || exit 1
