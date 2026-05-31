# Traefik Configuration Structure

## Overview
Traefik dynamic configuration is now organized by domain/website project.

## Directory Structure

```
/root/site/
├── compose/
│   └── traefik/
│       ├── traefik.yml                    # Static configuration (watches all .yml files in dynamic/)
│       └── dynamic/
│           ├── README.md                  (this file)
│           ├── ctc-research.yml           # ctc-research.com routers & services
│           ├── structa-cloud.yml          # core.structa.cloud routers & services
│           ├── catchall.yml               # Catchall routers
│           ├── middlewares.yml            # Common middlewares
│           ├── docs.yml                   # Documentation routers
│           └── traefik-dashboard.yml      # Dashboard configuration
```

## File Descriptions

### Website Configurations (websites/compose/traefik/dynamic/)

#### ctc-research.yml
- **Domain:** ctc-research.com, www.ctc-research.com, arch.ctc-research.com
- **Routers:**
  - `ctc-media-http`: HTTP → HTTPS redirect for /static/ and /media/
  - `ctc-media-https`: HTTPS for /static/ and /media/ files
  - `ctc-site-https`: HTTPS for main site (port 5070)
- **Services:**
  - `ctc-site-service`: Django backend on ctc-research-website:5070
  - `ctc-media-service`: Nginx static/media on ctc-research-media:80

#### structa-cloud.yml
- **Domain:** core.structa.cloud, structa.cloud, www.structa.cloud
- **Routers:**
  - `structa-media-http`: HTTP → HTTPS redirect for /static/ and /media/
  - `structa-media-https`: HTTPS for /static/ and /media/ files
  - `structa-site-https`: HTTPS for main site (port 5071)
- **Services:**
  - `structa-site-service`: Django backend on lms-demo-website:5071
  - `structa-media-service`: Nginx static/media on lms-demo-media:80

### VResume Project Configuration (compose/traefik/dynamic/)

#### vresume.yml
- **Domain:** vresume.structa.cloud, www.vresume.structa.cloud
- **Routers:**
  - `vresume-media-http`: HTTP → HTTPS redirect for /static/ and /media/
  - `vresume-media-https`: HTTPS for /static/ and /media/ files
  - `vresume-site-https`: HTTPS for main site (port 5072)
- **Services:**
  - `vresume-site-service`: Django backend on vresume-website:5072
  - `vresume-media-service`: Nginx static/media on vresume-media:80

## How Traefik Loads Configuration

1. Traefik reads static config from `traefik.yml`
2. Static config enables file provider at `/etc/traefik/dynamic`
3. File provider watches directory recursively:
   - Loads `ctc-research.yml` from `/etc/traefik/dynamic/`
   - Loads `structa-cloud.yml` from `/etc/traefik/dynamic/`
   - Loads `vresume.yml` from `/etc/traefik/dynamic/`
   - Loads common configs (catchall, middlewares, docs, dashboard)
4. Traefik combines all configurations and watches for changes

## Mount Points in Docker

In `/root/site/docker-compose.yml`, the traefik service mounts:
```yaml
volumes:
  - ./compose/traefik/traefik.yml:/etc/traefik/traefik.yml:ro
  - ./compose/traefik/dynamic:/etc/traefik/dynamic:ro
```

This creates the directory structure:
```
/etc/traefik/
├── traefik.yml
└── dynamic/
    ├── ctc-research.yml
    ├── structa-cloud.yml
    ├── (other common configs)
    └── vresume/
        └── vresume.yml
```

## SSL Certificates

All domains use Let's Encrypt with the `letsencrypt` resolver:
- **Staging:** `https://acme-staging-v02.api.letsencrypt.org/directory` (default, for testing)
- **Production:** `https://acme-v02.api.letsencrypt.org/directory` (change in traefik.yml when ready)

Each domain defines its main domain and SANs (Subject Alternative Names):
- ctc-research.com: main, sans: [www, arch]
- structa.cloud: main, sans: [*.structa.cloud, www, core]
- vresume.structa.cloud: main, sans: [www.vresume.structa.cloud]

## Health Checks

Each Django service includes a health check:
- **ctc-research-website:** Path `/` on port 5070, Host: ctc-research.com
- **lms-demo-website:** Path `/` on port 5071, Host: core.structa.cloud
- **vresume-website:** Path `/` on port 5072, Host: vresume.structa.cloud

Health checks run every 30 seconds with 10-second timeout.

## Common Configurations

### middlewares.yml
Defines reusable middlewares:
- `compress`: Gzip compression for responses
- `redirect-to-https`: HTTP → HTTPS redirect
- `security-headers`: Security headers
- `csrf-headers`: CSRF protection headers

### catchall.yml
Fallback router for unmapped domains.

### docs.yml & traefik-dashboard.yml
Documentation and dashboard configurations.

## Adding a New Domain

To add a new domain, create a new file in the appropriate directory:

**For websites project:**
```
/root/site/websites/compose/traefik/dynamic/newdomain.yml
```

**For VResume project:**
```
/root/site/compose/traefik/dynamic/newdomain.yml
```

Then use this template:
```yaml
http:
  routers:
    newdomain-media-http:
      rule: "Host(`newdomain.com`) && (PathPrefix(`/static/`) || PathPrefix(`/media/`))"
      entryPoints: [web]
      middlewares: [compress, redirect-to-https]
      service: newdomain-media-service
      priority: 100

    newdomain-media-https:
      rule: "Host(`newdomain.com`) && (PathPrefix(`/static/`) || PathPrefix(`/media/`))"
      entryPoints: [web-secure]
      middlewares: [compress, security-headers]
      service: newdomain-media-service
      priority: 100
      tls:
        certResolver: letsencrypt

    newdomain-site-https:
      rule: "Host(`newdomain.com`)"
      entryPoints: [web-secure]
      middlewares: [compress, csrf-headers, security-headers]
      service: newdomain-site-service
      tls:
        certResolver: letsencrypt

  services:
    newdomain-site-service:
      loadBalancer:
        servers:
          - url: "http://newdomain-website:5073"
        healthCheck:
          path: /
          interval: 30s
          timeout: 10s
          headers:
            Host: "newdomain.com"
            X-Forwarded-Proto: "https"

    newdomain-media-service:
      loadBalancer:
        servers:
          - url: "http://newdomain-media:80"
```

Traefik will automatically reload and apply the new configuration.
