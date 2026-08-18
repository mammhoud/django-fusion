FROM docker.io/traefik:latest

# Install utilities
RUN apk add --no-cache apache2-utils curl

# Create required directories (certs + dynamic config mount target)
RUN mkdir -p /etc/traefik/certs /etc/traefik/dynamic

# Copy static configuration (dynamic.yml → dynamic.yml)
COPY ./configs/traefik/dynamic.yml /etc/traefik/dynamic.yml

# Dynamic router configs are provided at runtime by the compose mount
# ./configs/traefik/dynamic -> /etc/traefik/dynamic (see docker-compose.traefik.yml).

# Copy custom certificates (if any)
COPY ./data/certs/ /etc/traefik/

# Set ownership to non‑root user (UID 1000)
# RUN chown -R 1000:1000 /etc/traefik

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8080/ping || exit 1

# Switch to non‑root user
# USER 1000:1000
