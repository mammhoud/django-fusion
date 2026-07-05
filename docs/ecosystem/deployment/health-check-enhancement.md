# Health Check Enhancement

> Enhanced health check system for ctc-research.com and structa.cloud

**Date:** 2026-04
**Status:** Complete

## Overview

Comprehensive health monitoring with homepage verification, asset checks, and Docker integration.

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health/` | Main health + homepage check |
| `GET /health/database/` | Database connectivity |
| `GET /health/assets/` | Static assets verification |
| `GET /health/media/` | Media files verification |

**Ports:** CTC on `5070`, Structa on `5071`

## Response Format

### Main Health (`/health/`)

```json
{
  "status": "healthy",
  "service": "django-app",
  "version": "1.0.0",
  "homepage": {
    "status": "ok",
    "status_code": 200,
    "has_content": true,
    "content_length": 163
  }
}
```

### Assets Health (`/health/assets/`)

```json
{
  "status": "healthy",
  "checks": {
    "static_root": {"status": "ok", "path": "/app/assets/staticfiles", "file_count": 1904},
    "webpack_bundles": {"status": "ok", "path": "/bundles/app/bundles.json", "exists": true},
    "bundle_files": {"status": "ok", "path": "/app/assets/bundles", "js_count": 131, "css_count": 5}
  }
}
```

## Status Levels

| Status | Meaning |
|--------|---------|
| `healthy` | All checks passed |
| `degraded` | Running with warnings (non-critical) |
| `unhealthy` | Critical errors — returns HTTP 503 |

## Docker Health Check Configuration

```yaml
# docker-compose.yml
healthcheck:
  interval: 60s      # was 30s — reduced overhead
  timeout: 10s
  retries: 3
  start_period: 120s # was 90s — allows slower startups
```

## Implementation

**Location:** `libs/django-fusion/src/django_fusion/health/views.py`

### Main check features
- Homepage load verification
- Content validation (>100 bytes)
- Detailed status codes

### Assets check features
- Static root directory + file count
- `bundles.json` validation
- JS/CSS bundle file counts

## Scripts

```bash
# Run all health checks
make health-check
# or
bash scripts/health-check.sh

# Hot-update health views in running containers
bash scripts/update-health-views.sh
```

## Testing

```bash
curl -s http://localhost:5070/health/ | jq .
curl -s http://localhost:5070/health/assets/ | jq .
curl -s http://localhost:5071/health/ | jq .
curl -s http://localhost:5071/health/assets/ | jq .
```

## Related

- [Nginx Assets Configuration](../../infrastructure/nginx/assets-configuration.md)
- [Health Check Quick Reference](../../shared/testing/health_check_quick_reference.md)
- [Deployment Overview](01_deployment_overview.md)
