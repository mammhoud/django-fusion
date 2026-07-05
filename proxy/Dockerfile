FROM docker.io/traefik:latest

# Install utilities
RUN apk add --no-cache apache2-utils curl

# Create required directories (static certs only — ACME disabled, see proxy/traefik/dynamic/certs.yml)
RUN mkdir -p /etc/traefik/certs /etc/traefik/dynamic

# Copy static configuration (dynamic.yml → dynamic.yml)
COPY ./traefik/dynamic.yml /etc/traefik/dynamic.yml

# (Optional) Copy dynamic config files if you have them
# If you prefer to mount them as a volume, skip this and mount ./traefik/dynamic
COPY ./traefik/*.yml /etc/traefik/dynamic/

# Copy custom certificates (if any)
COPY ./certs/ /etc/traefik/

# Set ownership to non‑root user (UID 1000)
# RUN chown -R 1000:1000 /etc/traefik

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8080/ping || exit 1

# Switch to non‑root user
# USER 1000:1000
