FROM docker.io/traefik:3.4.0

# Install apache2-utils for htpasswd
RUN apk add --no-cache apache2-utils

# Create ACME directory with proper permissions
RUN mkdir -p /etc/traefik/acme \
    && touch /etc/traefik/acme/acme.json \
    && chmod 600 /etc/traefik/acme/acme.json

# Copy static configuration (dynamic dir is volume-mounted at runtime)
COPY compose/traefik/traefik.yml /etc/traefik/traefik.yml

# Health check — Traefik 3.x uses /ping endpoint
HEALTHCHECK --interval=60s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ping || exit 1
