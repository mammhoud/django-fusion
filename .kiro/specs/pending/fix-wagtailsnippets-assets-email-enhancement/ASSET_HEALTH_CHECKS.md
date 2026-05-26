# Asset Health Checks Implementation

**Date**: April 6, 2026
**Task**: 2.4 - Implement asset health checks
**Status**: Complete

---

## Overview

This document describes the asset health check system implemented for both ctc-research.com and structa.cloud projects. The system provides comprehensive monitoring of static files, media files, and webpack bundles.

---

## Components

### 1. Health Check Endpoints

#### Endpoint: `/health/assets/`

**Purpose**: Provides detailed health status for all asset-related components.

**Response Format**:
```json
{
  "status": "ok|degraded|unhealthy",
  "checks": {
    "static_root": {
      "status": "ok|warning|error",
      "path": "/app/assets/staticfiles",
      "readable": true
    },
    "media_root": {
      "status": "ok|warning|error",
      "path": "/app/assets/media",
      "readable": true
    },
    "webpack_bundles": {
      "status": "ok|warning|error",
      "path": "/app/assets/bundles/bundles.json",
      "asset_count": 42
    },
    "bundle_files": {
      "status": "ok|warning",
      "path": "/app/assets/bundles",
      "file_count": 15
    }
  },
  "warnings": [
    "Media root directory not found: /app/assets/media"
  ],
  "errors": []
}
```

**HTTP Status Codes**:
- `200 OK`: Status is "ok" or "degraded"
- `503 Service Unavailable`: Status is "unhealthy"

**Implementation Files**:
- `ctc-research.com/apps/handlers/site/asset_health.py`
- `structa.cloud/apps/handlers/site/asset_health.py`

**URL Configuration**:
- `ctc-research.com/core/urls.py`
- `structa.cloud/apps/handlers/urls.py`

---

### 2. Deployment Validation

#### Management Command: `verify_deployment`

**Purpose**: Validates deployment health including asset availability.

**Usage**:
```bash
# ctc-research.com
cd ctc-research.com
uv run python manage.py verify_deployment

# structa.cloud
cd structa.cloud
uv run python manage.py verify_deployment --container alliance-website
```

**Check 9: Asset Health**

The verify_deployment command now includes a comprehensive asset health check that:
1. Calls the `/health/assets/` endpoint
2. Validates static files directory
3. Validates media files directory
4. Validates webpack bundles
5. Reports detailed status for each component

**Output Example**:
```
9. Checking Asset Health...
✓ Asset health check: OK
✓   Static files: OK
!   Media files: WARNING
✓   Webpack bundles: OK (42 assets)
```

**Implementation Files**:
- `ctc-research.com/apps/handlers/management/commands/verify_deployment.py`
- `structa.cloud/apps/handlers/management/commands/verify_deployment.py`

---

### 3. Production Monitoring

#### Monitoring Script: `compose/monitor_assets.py`

**Purpose**: Continuous monitoring of asset availability in production.

**Features**:
- Periodic health checks (configurable interval)
- Alert on failures and degraded status
- Logging to file and stdout
- Metrics tracking (uptime, failure count)
- Support for both sites

**Usage**:
```bash
# Monitor ctc-research.com
python compose/monitor_assets.py --site website --interval 300

# Monitor structa.cloud
python compose/monitor_assets.py --site core --interval 300

# Alert on degraded status
python compose/monitor_assets.py --site website --alert-on-degraded

# Custom log file
python compose/monitor_assets.py --site core --log-file /var/log/asset_monitor.log
```

**Options**:
- `--site`: Site to monitor (website, core, or all)
- `--interval`: Check interval in seconds (default: 300)
- `--alert-on-degraded`: Send alerts when status is degraded
- `--log-file`: Path to log file

**Log Files**:
- Default location: `compose/logs/asset_monitor_{site}.log`
- Format: Timestamped entries with level (INFO, WARNING, ERROR)

**Metrics**:
- Total checks performed
- Failure count
- Degraded count
- Uptime percentage

---

## Health Check Logic

### Status Determination

The asset health check endpoint determines overall status based on individual component checks:

1. **OK**: All components are functioning correctly
   - Static root exists and is readable
   - Media root exists and is readable
   - Webpack bundles.json is valid
   - Bundle files are present

2. **DEGRADED**: Some components have warnings but system is functional
   - Media root not found (expected in some configurations)
   - Webpack bundles not configured
   - Bundle files directory empty

3. **UNHEALTHY**: Critical components are failing
   - Static root not found or not readable
   - Webpack bundles.json is invalid or corrupted
   - Critical errors in asset loading

### Component Checks

#### 1. Static Root Check
- **Path**: `settings.STATIC_ROOT`
- **Validation**: Directory exists and is readable
- **Failure Impact**: UNHEALTHY (critical)

#### 2. Media Root Check
- **Path**: `settings.MEDIA_ROOT`
- **Validation**: Directory exists and is readable
- **Failure Impact**: DEGRADED (warning)
- **Note**: Media may be served by separate nginx container

#### 3. Webpack Bundles Check
- **Path**: `settings.WEBPACK_LOADER['DEFAULT']['STATS_FILE']`
- **Validation**: File exists and contains valid JSON
- **Failure Impact**: DEGRADED (warning)
- **Metrics**: Reports asset count from bundles.json

#### 4. Bundle Files Check
- **Path**: `{STATIC_ROOT}/../bundles/`
- **Validation**: Directory exists and contains .js files
- **Failure Impact**: DEGRADED (warning)
- **Metrics**: Reports file count

---

## Testing

### Manual Testing

#### Test Health Endpoint
```bash
# ctc-research.com
curl -s http://localhost:8270/health/assets/ | jq

# structa.cloud
curl -s http://localhost:8280/health/assets/ | jq
```

#### Test Deployment Validation
```bash
# ctc-research.com
cd ctc-research.com
uv run python manage.py verify_deployment

# structa.cloud
cd structa.cloud
uv run python manage.py verify_deployment
```

### Automated Testing

**Test File**: `tests/test_asset_health_check.py`

**Test Cases**:
1. `test_asset_health_endpoint_exists`: Verifies endpoint returns 200 or 503
2. `test_asset_health_checks_structure`: Validates response structure
3. `test_asset_health_status_codes`: Verifies correct HTTP status codes

**Run Tests**:
```bash
pytest tests/test_asset_health_check.py -v
```

---

## Integration with Existing Systems

### 1. Docker Health Checks

The asset health endpoint can be integrated into Docker health checks:

```yaml
services:
  website:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5070/health/assets/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2. Traefik Health Checks

Traefik can use the endpoint for backend health monitoring:

```yaml
http:
  services:
    website:
      loadBalancer:
        healthCheck:
          path: /health/assets/
          interval: 30s
          timeout: 10s
```

### 3. Monitoring Systems

The endpoint can be integrated with monitoring systems:
- **Prometheus**: Scrape endpoint and convert to metrics
- **Nagios/Icinga**: Use check_http plugin
- **Datadog**: Custom check using requests library
- **New Relic**: Synthetic monitoring

---

## Troubleshooting

### Common Issues

#### 1. Endpoint Returns 404

**Cause**: URL routing not configured or container not restarted

**Solution**:
```bash
# Restart container to pick up new code
docker-compose restart website
docker-compose restart alliance-website
```

#### 2. Static Root Not Found

**Cause**: Static files not collected

**Solution**:
```bash
# Collect static files
cd ctc-research.com
uv run python manage.py collectstatic --noinput
```

#### 3. Media Root Warning

**Cause**: Media directory not created or nginx media server not running

**Solution**:
```bash
# Check if media directory exists
docker exec website ls -la /app/assets/media

# Check if nginx media server is running
docker ps | grep media
```

#### 4. Webpack Bundles Not Found

**Cause**: Webpack build not run or bundles.json not generated

**Solution**:
```bash
# Run webpack build
cd ctc-research.com
npm run build

# Check bundles.json
cat ctc-research.com/assets/bundles/bundles.json
```

---

## Future Enhancements

### 1. Prometheus Metrics Export

Add `/metrics` endpoint that exports asset health as Prometheus metrics:

```python
# Example metrics
asset_health_status{site="website"} 1  # 1=ok, 0.5=degraded, 0=unhealthy
asset_static_files_count{site="website"} 42
asset_media_files_count{site="website"} 128
asset_webpack_bundles_count{site="website"} 15
```

### 2. Alert Integration

Integrate with alerting systems:
- Email alerts on failures
- Slack notifications
- PagerDuty integration
- SMS alerts for critical failures

### 3. Historical Metrics

Store health check history:
- Database storage of check results
- Trend analysis
- Uptime reports
- Performance metrics

### 4. Asset Integrity Checks

Add checksums and integrity validation:
- Verify file checksums
- Detect corrupted assets
- Validate asset signatures
- Check for missing dependencies

---

## Maintenance

### Log Rotation

Configure log rotation for monitoring logs:

```bash
# /etc/logrotate.d/asset-monitor
/root/site/compose/logs/asset_monitor_*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### Monitoring Service

Create systemd service for continuous monitoring:

```ini
# /etc/systemd/system/asset-monitor-website.service
[Unit]
Description=Asset Monitor for ctc-research.com
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/site
ExecStart=/usr/bin/python3 /root/site/compose/monitor_assets.py --site website --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable asset-monitor-website
systemctl start asset-monitor-website
systemctl status asset-monitor-website
```

---

## Conclusion

The asset health check system provides comprehensive monitoring of static files, media files, and webpack bundles for both ctc-research.com and structa.cloud. The system includes:

1. ✅ Health check endpoints at `/health/assets/`
2. ✅ Integration with deployment validation
3. ✅ Production monitoring script
4. ✅ Comprehensive testing
5. ✅ Documentation and troubleshooting guides

The system is ready for production use and can be extended with additional features as needed.
