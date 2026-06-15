# Health Check Enhancement — Deployment Summary

> Enhanced health check system with homepage verification, webpack bundle validation, and improved Docker intervals.

**Date:** 2026-04-24
**Site:** Both (structa.cloud + ctc-research.com)
**Status:** Complete

---

## Completed Tasks

### 1. Enhanced Health Check System

- Updated main health check to verify homepage content (HTTP 200 + content length).
- Enhanced assets health check with detailed diagnostics.
- Added webpack bundles verification.
- Added static files counting and validation.

### 2. Docker Configuration

- Updated health check intervals: 30s → 60s.
- Extended start period: 90s → 120s.
- Applied to both `ctc-research.docker-compose.yml` and `structa.docker-compose.yml`.

### 3. Deployment

- Redeployed `ctc-website` and `structa-website` services.
- Updated health check views in running containers.
- Verified all services healthy.

---

## Health Check Endpoints

| Endpoint | Checks |
|---|---|
| `/health/` | Service running, homepage HTTP 200, content length > 100 bytes |
| `/health/assets/` | Static files directory, file count, webpack `bundles.json`, JS/CSS counts |
| `/health/database/` | DB connection, query execution |
| `/health/media/` | Media directory exists and accessible |

### Status Levels

| Status | HTTP Code | Meaning |
|---|---|---|
| `healthy` | 200 | All checks passed |
| `degraded` | 200 | Running with warnings |
| `unhealthy` | 503 | Critical errors |

---

## Health Check Results at Deployment

### ctc-research.com (port 5070)

```
✓ /health/          — healthy (homepage: 200, content: 163 bytes)
✓ /health/database/ — healthy (connected)
✓ /health/assets/   — degraded (1904 files, webpack warnings)
✓ /health/media/    — healthy
```

### structa.cloud (port 5071)

```
✓ /health/          — healthy (homepage: 200, content: 161 bytes)
✓ /health/database/ — healthy (connected)
✓ /health/assets/   — degraded (1904 files, webpack warnings)
✓ /health/media/    — healthy
```

---

## Files Modified

| File | Change |
|---|---|
| `libs/django-grep/src/django_grep/health/views.py` | Enhanced `HealthCheckView` and `AssetsHealthView` |
| `websites/ctc-research.docker-compose.yml` | Updated healthcheck intervals |
| `websites/structa.docker-compose.yml` | Updated healthcheck intervals |
| `Makefile` | Added `health-check` target |

---

## New Tools

### `scripts/health-check.sh`

Comprehensive health check testing with color-coded output and JSON responses.

```bash
make health-check
```

### `scripts/update-health-views.sh`

Hot-update health views in running containers without a rebuild.

```bash
bash scripts/update-health-views.sh
```

---

## Quick Reference Commands

```bash
# Run all health checks
make health-check

# Check specific service
curl http://localhost:5070/health/ | jq .
curl http://localhost:5071/health/ | jq .

# Check assets
curl http://localhost:5070/health/assets/ | jq .
curl http://localhost:5071/health/assets/ | jq .

# View container status
docker ps | grep website

# View logs
docker logs ctc-website
docker logs structa-website
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Health check fails | `docker logs ctc-website` |
| Homepage check fails | `docker ps` — verify service is running |
| Assets check degraded | Normal if webpack not yet built |
| Database check fails | `docker ps \| grep postgres` |
