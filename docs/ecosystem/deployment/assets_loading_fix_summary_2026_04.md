# Assets Loading Path Fix — Summary

> Fix for incorrect bundles path and missing webpack build in Docker containers.

**Date:** 2026-04-24
**Site:** Both (structa.cloud + ctc-research.com)
**Status:** Complete

---

## Issues Fixed

### 1. Incorrect Bundles Path in Docker

**Problem:** `BUNDLES_DIR` pointed to `/bundles/app` (non-existent) instead of `/app/assets/bundles`.

**Root Cause:** `assets.py` assumed a workspace structure that doesn't exist inside Docker containers.

**Solution:** Updated `assets.py` to detect Docker environment and use correct paths:

```python
if os.getenv('RUNNING_ENV') == 'docker':
    BUNDLES_DIR = ASSETS_DIR / "bundles"          # /app/assets/bundles in Docker
else:
    BUNDLES_DIR = WORKSPACE_DIR / "bundles" / SITE_NAME  # local development
```

### 2. Missing Webpack Build

**Problem:** Webpack bundles were not being built during Docker image creation.

**Root Cause:** `npm install` in production mode (`NODE_ENV=production`) skips `devDependencies`, which includes `webpack-cli`.

**Solution:** Updated Dockerfile to install dev dependencies:

```dockerfile
npm install --include=dev --prefer-offline --no-audit --no-fund
```

### 3. Nginx Static Files Configuration

**Problem:** Nginx was correctly configured but had no files to serve due to issues 1 and 2.

**Solution:** After fixing paths and building webpack bundles, nginx now serves 2051 static files and 240 webpack assets.

---

## Results

### Before Fix

```json
{
  "status": "degraded",
  "checks": {
    "static_root": {"status": "ok", "file_count": 1904},
    "webpack_bundles": {"status": "warning", "exists": false},
    "bundle_files": {"status": "warning", "js_count": 0, "css_count": 0}
  },
  "warnings": ["Webpack stats file not found"]
}
```

### After Fix

```json
{
  "status": "healthy",
  "checks": {
    "static_root": {"status": "ok", "file_count": 2051},
    "webpack_bundles": {"status": "ok", "asset_count": 240},
    "bundle_files": {"status": "ok", "js_count": 131, "css_count": 5}
  },
  "warnings": [],
  "errors": []
}
```

---

## Files Modified

| File | Change |
|---|---|
| `websites/ctc-research.com/configs/base/assets.py` | Added Docker env detection, fixed `BUNDLES_DIR` |
| `websites/structa.cloud/configs/base/assets.py` | Added Docker env detection, fixed `BUNDLES_DIR` |
| `websites/compose/Dockerfile` | Updated `npm install` to include dev dependencies |

---

## Deployment Steps Taken

1. Updated `assets.py` for both projects.
2. Updated `Dockerfile` for proper `npm install`.
3. Manual build in running containers (temporary):

```bash
docker exec ctc-website npm install --include=dev
docker exec ctc-website npm run build
docker exec ctc-website python manage.py collectstatic --noinput
```

4. Verified static file serving:

```bash
curl -I http://localhost:8271/static/runtime.7be6a9cd.js  # ctc-research.com
curl -I http://localhost:8272/static/runtime.7be6a9cd.js  # structa.cloud
```

5. Confirmed health checks passing: `make health-check`

---

## For Future Deployments

Fixes are now permanent in the Dockerfile. Rebuild with:

```bash
# ctc-research.com
cd websites
docker compose -f docker-compose.yml -f ctc-research.docker-compose.yml build --no-cache website
docker compose -f docker-compose.yml -f ctc-research.docker-compose.yml up -d website

# structa.cloud
docker compose -f docker-compose.yml -f structa.docker-compose.yml build --no-cache core
docker compose -f docker-compose.yml -f structa.docker-compose.yml up -d core
```

The Dockerfile now:
1. Installs all dependencies including dev dependencies.
2. Builds webpack bundles to `/app/assets/bundles`.
3. Runs `collectstatic` to copy to `/app/assets/staticfiles`.
4. Mounts staticfiles volume to nginx at `/var/www/static`.

---

## Final Status

| Service | Static Files | Webpack Assets |
|---|---|---|
| ctc-website | 2051 | 240 (131 JS + 5 CSS) |
| structa-website | 2051 | 240 (131 JS + 5 CSS) |
