# Nginx Assets Configuration

> Static and media file serving for ctc-research.com and structa.cloud

**Date:** 2026-04
**Status:** Complete

## Overview

Nginx serves static and media files for both sites, providing optimized delivery with caching and compression.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Django App     │────────▶│  Shared Volume   │◀────────│  Nginx Server   │
│  (ctc-website)  │         │  website_static  │         │  (ctc-media)    │
│                 │         │                  │         │                 │
│  Builds assets  │         │   /app/assets/   │         │   /var/www/     │
│  Collects       │         │    staticfiles    │         │    static/      │
│  static files   │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                                                   │
                                                                   ▼
                                                          Serves via HTTP
                                                          Port 8271 (CTC)
                                                          Port 8272 (Structa)
```

## Volume Mapping

### ctc-research.com
```yaml
volumes:
  website_static:
    external: true
    name: website_static
  website_media:
    external: true
    name: website_media

services:
  ctc-website:
    volumes:
      - website_static:/app/assets/staticfiles:z
      - website_media:/app/assets/media:z

  ctc-website-media:
    volumes:
      - website_static:/var/www/static:ro
      - website_media:/var/www/media:ro
```

### structa.cloud
Same volume structure, different containers:
- `structa-website` → Django app
- `structa-website-media` → Nginx server

## Nginx Configuration

**Location:** `compose/nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript
               application/javascript application/xml application/json
               image/svg+xml;

    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff";
        access_log off;
        try_files $uri $uri/ =404;
    }

    location /media/ {
        alias /var/www/media/;
        expires 30d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options "nosniff";
        access_log off;
        try_files $uri $uri/ =404;
    }

    location / {
        return 404;
    }
}
```

## Django Static Files Configuration

**Location:** `websites/*/configs/base/assets.py`

```python
if os.getenv('RUNNING_ENV') == 'docker':
    BUNDLES_DIR = ASSETS_DIR / "bundles"
else:
    BUNDLES_DIR = WORKSPACE_DIR / "bundles" / SITE_NAME

STATIC_ROOT = str(STATICFILES_DIR)   # /app/assets/staticfiles
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BUNDLES_DIR)]
```

## Asset Build Process

```bash
# 1. Webpack build
npm run build   # → /app/assets/bundles

# 2. Collect static files
python manage.py collectstatic --noinput
# bundles + app statics → /app/assets/staticfiles

# 3. Nginx reads from shared volume
# /var/www/static/ ← website_static ← /app/assets/staticfiles
```

## File Paths Reference

| Context | Bundles | Static Root | Nginx Path |
|---------|---------|-------------|------------|
| Django Container | `/app/assets/bundles` | `/app/assets/staticfiles` | N/A |
| Nginx Container | N/A | N/A | `/var/www/static` |
| Volume | `website_static` | `website_static` | `website_static` |
| URL | N/A | `/static/` | `/static/` |

## Ports

| Service | Port | Purpose |
|---------|------|---------|
| ctc-website | 5070 | Django application |
| ctc-website-media | 8271 | Static/media files |
| structa-website | 5071 | Django application |
| structa-website-media | 8272 | Static/media files |

## Testing

```bash
# Via nginx
curl -I http://localhost:8271/static/runtime.7be6a9cd.js   # CTC
curl -I http://localhost:8272/static/runtime.7be6a9cd.js   # Structa

# Assets health check
curl http://localhost:5070/health/assets/ | jq .
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "static_root": {"status": "ok", "file_count": 2051},
    "webpack_bundles": {"status": "ok", "asset_count": 240},
    "bundle_files": {"status": "ok", "js_count": 131, "css_count": 5}
  }
}
```

## Troubleshooting

### 404 on Static Files

```bash
# Check files in Django container
docker exec ctc-website ls -la /app/assets/staticfiles/

# Check files in Nginx container
docker exec ctc-website-media ls -la /var/www/static/

# Check volume mount
docker inspect ctc-website | grep -A 10 Mounts
```

### Webpack Bundles Missing

```bash
docker exec ctc-website ls -la /app/assets/bundles/
docker exec ctc-website python manage.py collectstatic --noinput
docker exec ctc-website npm run build
```

### Nginx Not Serving

```bash
docker exec ctc-website-media nginx -t
docker logs ctc-website-media
docker restart ctc-website-media
```

## Performance

| Feature | Setting |
|---------|---------|
| Gzip | Enabled for CSS, JS, JSON, SVG |
| Static cache | 1 year (immutable) |
| Media cache | 30 days |
| Access logs | Disabled for static/media |
| Security | `X-Content-Type-Options: nosniff` |

## Related

- [Nginx README](README.md)
- [Health Check Enhancement](../../ecosystem/deployment/health-check-enhancement.md)
- [Docker Setup](../docker/)
