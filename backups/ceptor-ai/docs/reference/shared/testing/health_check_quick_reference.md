# Health Check Quick Reference

> Fast lookup for health check endpoints, commands, and response formats.

**Date:** 2026-04-24
**Site:** Both (structa.cloud + ctc-research.com)
**Status:** Current

---

## Quick Commands

```bash
# Run all health checks
make health-check

# Main health (includes homepage check)
curl http://localhost:5070/health/ | jq .   # ctc-research.com
curl http://localhost:5071/health/ | jq .   # structa.cloud

# Assets health
curl http://localhost:5070/health/assets/ | jq .
curl http://localhost:5071/health/assets/ | jq .

# Database health
curl http://localhost:5070/health/database/ | jq .
curl http://localhost:5071/health/database/ | jq .

# Media health
curl http://localhost:5070/health/media/ | jq .
curl http://localhost:5071/health/media/ | jq .
```

---

## Endpoints

| Service | Port | `/health/` | `/health/assets/` | `/health/database/` | `/health/media/` |
|---|---|---|---|---|---|
| ctc-research.com | 5070 | ✅ | ✅ | ✅ | ✅ |
| structa.cloud | 5071 | ✅ | ✅ | ✅ | ✅ |

---

## What Each Endpoint Checks

### `/health/`
- Service is running
- Homepage loads (HTTP 200)
- Homepage has content (> 100 bytes)
- Content length reported

### `/health/assets/`
- Static files directory exists
- Static files count
- Webpack `bundles.json` validation
- Bundle files (JS/CSS) count

### `/health/database/`
- Database connection
- Query execution

### `/health/media/`
- Media directory exists
- Media directory accessible

---

## Status Levels

| Status | HTTP Code | Meaning |
|---|---|---|
| `healthy` | 200 | All checks passed |
| `degraded` | 200 | Running with warnings |
| `unhealthy` | 503 | Critical errors |

---

## Example Responses

### Healthy

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

### Degraded

```json
{
  "status": "degraded",
  "checks": {
    "static_root": {"status": "ok"},
    "webpack_bundles": {"status": "warning"}
  },
  "warnings": ["Webpack stats file not found"],
  "errors": []
}
```

### Unhealthy

```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "connection refused"
}
```

---

## Maintenance

```bash
# Update health views in running containers (no rebuild)
bash scripts/update-health-views.sh

# Restart services
docker restart ctc-website structa-website

# View logs
docker logs ctc-website
docker logs structa-website

# Check container health status
docker ps | grep website
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Health check fails | `docker logs ctc-website` |
| Homepage check fails | `docker ps` — verify service is running |
| Assets check degraded | Normal if webpack not yet built; run `make rebuild svc=website` |
| Database check fails | `docker ps \| grep postgres` — check postgres container |

---

## Related Docs

- [Health Check Enhancement Summary](../../../guides/deployment/health_check_enhancement_summary_2026_04.md)
- [Assets Loading Fix Summary](../../../guides/deployment/assets_loading_fix_summary_2026_04.md)
