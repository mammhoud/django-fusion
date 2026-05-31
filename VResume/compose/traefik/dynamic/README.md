# VResume Traefik Configuration

## Overview
VResume project-specific Traefik configuration for the vresume.structa.cloud domain.

## Directory Structure

```
VResume/compose/traefik/
├── dynamic/
│   ├── README.md (this file)
│   └── vresume-structa.yml
```

## Configuration Files

### vresume-structa.yml
Traefik routers and backend services for vresume.structa.cloud

**Domain:** vresume.structa.cloud, www.vresume.structa.cloud

**Services:**
- Django application: vresume-website on port 5072
- Static/Media server: vresume-website-media on port 8273

**Features:**
- HTTP to HTTPS redirect
- Let's Encrypt SSL certificates
- Automatic health checks
- Security headers
- Gzip compression

## Integration with Main Traefik

This directory is mounted into the main Traefik container at:
```
/etc/traefik/dynamic/vresume
```

The main Traefik configuration (in `/root/site/compose/traefik/traefik.yml`) watches:
```
/etc/traefik/dynamic
```

This watches all files recursively, including this directory.

## Mount Point

In `/root/site/docker-compose.yml`:
```yaml
volumes:
  - ./VResume/compose/traefik/dynamic:/etc/traefik/dynamic/vresume:ro
```

## Docker Compose Integration

The VResume docker-compose file (`/root/site/VResume/compose/docker-compose.yml` or similar) defines:
- `vresume-website` service on port 5072
- `vresume-website-media` service on port 8273
- Both services connected to `traefik-net` network

Traefik routes traffic from vresume.structa.cloud to these services.

## Monitoring

View Traefik dashboard at: http://localhost:8080/dashboard/

You should see:
- Router: `vresume-site-https`
- Router: `vresume-media-https`
- Service: `vresume-site-service` (backend: vresume-website:5072)
- Service: `vresume-media-service` (backend: vresume-website-media:8273)
