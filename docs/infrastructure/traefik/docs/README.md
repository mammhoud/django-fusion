# Traefik Documentation

> Modern reverse proxy and load balancer

## Overview

Traefik handles incoming traffic, SSL termination, and routes requests to appropriate services.

## Architecture

```
Internet → Traefik (Port 80/443) → Services
                    ↓
            Dashboard (Port 8080)
```

## Configuration Files

```
traefik/
├── traefik.yml           # Main configuration
├── Dockerfile            # Container image
├── README.md             # This file
├── dynamic/              # Dynamic configuration
│   ├── cors.yaml         # CORS rules
│   ├── headers.yaml      # Security headers
│   └── middleware.yaml   # Custom middleware
└── docs/                 # Documentation
    ├── README.md
    └── _sidebar.md
```

## Main Configuration

```yaml
# traefik.yml
global:
  checkNewVersion: false
  sendAnonymousUsage: false

api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
    http3: {}

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: site_default
  file:
    directory: "/etc/traefik/dynamic"
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: "vresume@structa.cloud"
      storage: "/acme.json"
      httpChallenge:
        entryPoint: web

log:
  level: INFO
  format: json

metrics:
  prometheus:
    entryPoint: metrics
```

## Dynamic Configuration

```yaml
# dynamic/cors.yaml
http:
  middlewares:
    cors-header:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        accessControlAllowOrigins:
          - "*"
        accessControlMaxAge: 100
        addVaryHeader: true
```

```yaml
# dynamic/headers.yaml
http:
  middlewares:
    security-headers:
      headers:
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        forceSTSHeader: true
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customFrameOptionsValue: "SAMEORIGIN"
```

## Docker Labels

```yaml
# docker-compose.yml labels for services
services:
  ctc-research:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ctc-research.rule=Host(`ctc.research.com`)"
      - "traefik.http.routers.ctc-research.entrypoints=websecure"
      - "traefik.http.routers.ctc-research.tls.certresolver=letsencrypt"
      - "traefik.http.services.ctc-research.loadbalancer.server.port=8000"
      - "traefik.http.middlewares.ctc-research-cors.headers.accessControlAllowOrigins=*"

  structa-cloud:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.structa-cloud.rule=Host(`structa.cloud`)"
      - "traefik.http.routers.structa-cloud.entrypoints=websecure"
      - "traefik.http.routers.structa-cloud.tls.certresolver=letsencrypt"
      - "traefik.http.services.structa-cloud.loadbalancer.server.port=8001"
```

## Quick Commands

```bash
# View dashboard
http://localhost:8080

# Check configuration
docker exec traefik traefik healthcheck

# View logs
docker logs -f traefik

# Reload configuration
docker exec traefik traefik ping
```

## Related Documentation

- [Nginx Documentation](../nginx/)
- [PostgreSQL Documentation](../postgres/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
