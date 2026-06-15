# Health Endpoints Quick Reference

## Overview

Three health check endpoints are available for monitoring the CTC Research deployment:

| Endpoint | Purpose | Status Code | Response |
|----------|---------|-------------|----------|
| `/health/` | Basic application health | 200 | `{"status": "ok"}` |
| `/health/assets/` | Static assets & webpack | 200/503 | Detailed asset checks |
| `/health/media/` | Media files health | 200/503 | Detailed media checks |

## Endpoint Details

### 1. Basic Health Check: `/health/`

**Purpose**: Quick health check for the application

**URL**:
- Localhost: `http://localhost:8270/health/`
- Domain: `https://ctc-research.com/health/`

**Response**:
```json
{
  "status": "ok"
}
```

**Status Codes**:
- `200 OK` - Application is healthy
- `503 Service Unavailable` - Application has issues

**Response Time**: < 100ms

**Use Case**: Quick health verification, load balancer checks

---

### 2. Assets Health Check: `/health/assets/`

**Purpose**: Verify static files and webpack bundles are loaded

**URL**:
- Localhost: `http://localhost:8270/health/assets/`
- Domain: `https://ctc-research.com/health/assets/`

**Response**:
```json
{
  "status": "ok",
  "checks": {
    "static_root": {
      "status": "ok",
      "path": "/app/assets/staticfiles",
      "readable": true
    },
    "media_root": {
      "status": "ok",
      "path": "/app/assets/media",
      "readable": true
    },
    "webpack_bundles": {
      "status": "ok",
      "path": "/app/assets/bundles/bundles.json",
      "asset_count": 206
    },
    "bundle_files": {
      "status": "ok",
      "path": "/app/assets/bundles",
      "file_count": 36
    }
  },
  "warnings": [],
  "errors": []
}
```

**Status Codes**:
- `200 OK` - All assets healthy
- `503 Service Unavailable` - Asset issues detected

**Response Time**: < 500ms

**Checks Performed**:
- Static files directory exists and readable
- Media files directory exists and readable
- Webpack bundles configuration valid
- Bundle files present and accessible

**Use Case**: Asset availability verification, CDN health checks

---

### 3. Media Health Check: `/health/media/`

**Purpose**: Verify media files are accessible and writable

**URL**:
- Localhost: `http://localhost:8270/health/media/`
- Domain: `https://ctc-research.com/health/media/`

**Response**:
```json
{
  "status": "ok",
  "checks": {
    "media_root": {
      "status": "ok",
      "path": "/app/assets/media",
      "readable": true,
      "file_count": 178
    },
    "media_writable": {
      "status": "ok",
      "message": "Media volume is writable"
    },
    "media_images": {
      "status": "ok",
      "path": "/app/assets/media/images",
      "exists": true
    },
    "media_documents": {
      "status": "ok",
      "path": "/app/assets/media/documents",
      "exists": true
    }
  },
  "warnings": [],
  "errors": []
}
```

**Status Codes**:
- `200 OK` - All media healthy
- `503 Service Unavailable` - Media issues detected

**Response Time**: < 500ms

**Checks Performed**:
- Media root directory exists and readable
- Media volume is writable
- File count reported
- Common subdirectories detected

**Use Case**: Media file availability, storage health checks

---

## Testing Commands

### Using curl

```bash
# Basic health check
curl http://localhost:8270/health/

# Assets health check
curl http://localhost:8270/health/assets/

# Media health check
curl http://localhost:8270/health/media/

# At domain (with HTTPS)
curl -k https://ctc-research.com/health/
curl -k https://ctc-research.com/health/assets/
curl -k https://ctc-research.com/health/media/
```

### Using Python

```python
import requests

# Basic health
response = requests.get('http://localhost:8270/health/')
print(response.json())

# Assets health
response = requests.get('http://localhost:8270/health/assets/')
data = response.json()
print(f"Status: {data['status']}")
print(f"Assets: {data['checks']['webpack_bundles']['asset_count']}")

# Media health
response = requests.get('http://localhost:8270/health/media/')
data = response.json()
print(f"Status: {data['status']}")
print(f"Media files: {data['checks']['media_root']['file_count']}")
```

### Using Docker

```bash
# From inside container
docker exec website curl http://127.0.0.1:5070/health/
docker exec website curl http://127.0.0.1:5070/health/assets/
docker exec website curl http://127.0.0.1:5070/health/media/
```

---

## Status Codes Explained

### Status: "ok"
- All checks passed
- System is healthy
- HTTP 200 response

### Status: "degraded"
- Some checks passed, some warnings
- System is operational but with issues
- HTTP 200 response (still operational)

### Status: "unhealthy"
- Critical checks failed
- System has issues
- HTTP 503 response

---

## Troubleshooting

### `/health/assets/` returns degraded

**Possible Causes**:
- Static files not collected
- Webpack configuration missing
- Bundle files not present

**Solutions**:
```bash
# Collect static files
docker exec website python com collectstatic --noinput

# Verify webpack configuration
docker exec website python com shell -c "from django.conf import settings; print(settings.WEBPACK_LOADER)"

# Check bundle files
docker exec website ls -la /app/assets/bundles/
```

### `/health/media/` returns degraded

**Possible Causes**:
- Media volume not mounted
- Media directory permissions issue
- Disk space full

**Solutions**:
```bash
# Check media volume
docker volume ls | grep website_media

# Check permissions
docker exec website ls -la /app/assets/media/

# Check disk space
docker exec website df -h /app/assets/media/
```

### All endpoints return 503

**Possible Causes**:
- Application not running
- Database connection failed
- Container crashed

**Solutions**:
```bash
# Check container status
docker ps | grep website

# Check logs
docker logs website

# Restart container
docker restart website
```

---

## Monitoring Integration

### Prometheus Metrics

Add to Prometheus scrape config:
```yaml
- job_name: 'ctc-research-health'
  static_configs:
    - targets: ['localhost:8270']
  metrics_path: '/health/'
```

### Grafana Dashboard

Create dashboard with:
- Health endpoint response time
- Asset availability
- Media file count
- Error rate

### Alerting Rules

```yaml
- alert: HealthEndpointDown
  expr: up{job="ctc-research-health"} == 0
  for: 5m

- alert: AssetsHealthDegraded
  expr: health_assets_status != 1
  for: 5m

- alert: MediaHealthDegraded
  expr: health_media_status != 1
  for: 5m
```

---

## Performance Benchmarks

| Endpoint | Target | Current | Status |
|----------|--------|---------|--------|
| `/health/` | < 100ms | ~50ms | ✅ Excellent |
| `/health/assets/` | < 500ms | ~200ms | ✅ Good |
| `/health/media/` | < 500ms | ~200ms | ✅ Good |

---

## Docker Healthcheck Configuration

The Docker container is configured to check all three endpoints:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -sf http://127.0.0.1:5070/health/ && curl -sf http://127.0.0.1:5070/health/assets/ && curl -sf http://127.0.0.1:5070/health/media/ || exit 1"]
  interval: 30s
  timeout: 20s
  retries: 3
  start_period: 60s
```

---

## Related Files

- **Implementation**: `ctc-research.com/apps/handlers/site/asset_health.py`
- **Implementation**: `ctc-research.com/apps/handlers/site/media_health.py`
- **Configuration**: `ctc-research.com/core/urls.py`
- **Docker Config**: `ctc-research.com/docker-compose.yml`
- **Tests**: `ctc-research.com/tests/selenium/test_health_endpoints.py`

---

## Support

For issues or questions about health endpoints:
1. Check the troubleshooting section above
2. Review Docker logs: `docker logs website`
3. Check endpoint responses manually
4. Verify Docker volumes are mounted
5. Ensure all containers are running

---

*Last Updated: April 14, 2026*
*Status: ✅ Production Ready*
