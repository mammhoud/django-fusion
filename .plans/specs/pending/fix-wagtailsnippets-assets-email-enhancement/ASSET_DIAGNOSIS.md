# Asset Loading Diagnosis Report - structa.cloud

**Date**: April 6, 2026
**Task**: 2.1 - Diagnose asset loading problems
**Status**: Investigation Complete

---

## Executive Summary

The investigation revealed that **static files (CSS/JS bundles) are loading correctly**, but **media files return 404 errors** on structa.cloud. The root cause is a missing nginx media server container in the production setup.

---

## 1. Current Asset Serving Setup

### 1.1 Static Files (✅ Working)
- **Status**: Working correctly
- **Served by**: WhiteNoise middleware + Django staticfiles
- **URL Pattern**: `/static/*`
- **Storage Location**: `/app/assets/staticfiles` (inside container)
- **Docker Volume**: `alliance_static`
- **Test Result**:
  ```bash
  curl -I http://localhost:8280/static/runtime.f6d46873.js
  # HTTP/1.1 200 OK
  ```

### 1.2 Media Files (❌ Not Working)
- **Status**: Returning 404 errors
- **Expected URL Pattern**: `/media/*`
- **Storage Location**: `/app/assets/media` (inside container)
- **Docker Volume**: `alliance_media`
- **Test Result**:
  ```bash
  curl -I http://localhost:8280/media/images/0823-DashboardDesign-Dan-Social_.2e16d0ba.fill-1920x1080.png
  # HTTP/1.1 404 Not Found
  ```

---

## 2. Configuration Analysis

### 2.1 Environment Settings
```env
SERVER_ENV=production
DEBUG=false
RUNNING_ENV=docker
```

**Issue**: With `DEBUG=false`, Django's development URL patterns (including media file serving) are NOT activated.

### 2.2 Django Settings

**File**: `structa.cloud/configs/base/assets.py`
```python
MEDIA_ROOT = str(MEDIA_DIR)  # /app/assets/media
MEDIA_URL = "/media/"
STATIC_ROOT = str(ASSETS_DIR / "staticfiles")
STATIC_URL = "/static/"
```

**File**: `structa.cloud/configs/base/middlewares.py`
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ Serves static files
    # ... other middleware
]
```

**Analysis**:
- WhiteNoise serves static files in production ✅
- WhiteNoise does NOT serve media files ❌
- Media files require separate nginx server or Django dev mode

### 2.3 URL Configuration

**File**: `structa.cloud/alliance/urls.py`
```python
if settings.DEBUG:
    from django_grep.contrib.debug_tools.dev_urls import configure_dev_urls
    urlpatterns = configure_dev_urls(urlpatterns, settings)
```

**Issue**: Since `DEBUG=false`, the `configure_dev_urls` function is never called, so media URL patterns are not added.

---

## 3. Comparison with ctc-research.com

### 3.1 ctc-research Setup (✅ Working)

**Docker Compose Structure**:
```yaml
services:
  website:
    # Django application
    volumes:
      - website_static:/app/assets/staticfiles:z
      - website_media:/app/assets/media:z

  website-media:
    # Nginx container for static/media files
    build:
      dockerfile: ./compose/nginx/Dockerfile
    volumes:
      - website_static:/var/www/static:ro
      - website_media:/var/www/media:ro
```

**Nginx Configuration** (`ctc-research.com/compose/nginx/nginx.conf`):
```nginx
server {
    listen 80;

    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://website:5070;
    }
}
```

### 3.2 structa.cloud Setup (❌ Missing Media Server)

**Docker Compose Structure**:
```yaml
services:
  core:
    # Django application only
    volumes:
      - alliance_static:/app/assets/staticfiles:rw
      - alliance_media:/app/assets/media:rw

  # ❌ NO nginx media server container!
```

**Missing Components**:
1. No `alliance-media` nginx container
2. No nginx Dockerfile in `structa.cloud/compose/`
3. No nginx configuration file

---

## 4. Webpack Configuration Issues

### 4.1 bundles.json Path Problem

**File**: `structa.cloud/assets/bundles/bundles.json`

**Issue**: Paths reference non-existent `/root/site/structa.cloud/core/` directory:
```json
{
  "assets": {
    "chunk/1942.ebef035a.chunk.js": {
      "path": "/root/site/structa.cloud/core/assets/bundles/chunk/1942.ebef035a.chunk.js",
      "publicPath": "/static/chunk/1942.ebef035a.chunk.js"
    }
  }
}
```

**Actual Path**: `/root/site/structa.cloud/assets/bundles/`

**Impact**:
- The `path` field is incorrect (references removed `core/` directory)
- The `publicPath` field is correct and working
- Django webpack-loader uses `publicPath`, so bundles still load correctly
- This is a **cosmetic issue** that should be fixed but doesn't break functionality

### 4.2 Webpack Configuration

**File**: `structa.cloud/webpack/main.config.js`

**Current Settings**:
```javascript
const staticUrl = '/static/';
const outputPath = path.resolve(__dirname, '../assets/bundles');

output: {
  path: outputPath,
  publicPath: `${staticUrl}`,
  filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
}
```

**Status**: ✅ Configuration is correct for static files

---

## 5. Bad Gateway Errors - Not Reproduced

### 5.1 Testing Results

**Attempted Tests**:
1. Homepage: `http://localhost:8280/` → ✅ 200 OK
2. Static CSS: `http://localhost:8280/static/css/vendors-49d0a293-0ad61438.332c3909.min.css` → ✅ 200 OK
3. Static JS: `http://localhost:8280/static/runtime.f6d46873.js` → ✅ 200 OK
4. Media file: `http://localhost:8280/media/images/...` → ❌ 404 Not Found
5. Admin page: `http://localhost:8280/admin/` → ✅ 302 Redirect (working)
6. Sign-in page: `http://localhost:8280/auth/sign-in/` → ✅ 200 OK with assets

**Conclusion**: No 502 Bad Gateway errors were encountered. The issue is **404 Not Found** for media files, not 502 errors.

### 5.2 Possible Scenarios for 502 Errors

502 Bad Gateway errors could occur in these scenarios:
1. **Traefik routing issues**: If Traefik cannot reach the backend container
2. **Container health check failures**: If the Django container is unhealthy
3. **Upstream connection failures**: If nginx tries to proxy to a dead Django container
4. **Missing nginx media server**: If Traefik routes to non-existent media server

**Current Status**: Container is healthy, Traefik is working, no 502 errors observed in local testing.

---

## 6. Root Causes Summary

### Primary Issues

1. **Missing nginx Media Server Container**
   - **Severity**: High
   - **Impact**: Media files return 404 in production
   - **Cause**: structa.cloud docker-compose.yml lacks `alliance-media` service
   - **Solution**: Add nginx container similar to ctc-research setup

2. **Production Mode Without Media Serving**
   - **Severity**: High
   - **Impact**: Django doesn't serve media files when DEBUG=false
   - **Cause**: Intentional Django design (media should be served by web server)
   - **Solution**: Add nginx media server (proper production setup)

### Secondary Issues

3. **Incorrect Paths in bundles.json**
   - **Severity**: Low
   - **Impact**: Cosmetic only, doesn't break functionality
   - **Cause**: Webpack output references old `core/` directory structure
   - **Solution**: Update webpack output path configuration

---

## 7. Recommended Solutions

### Solution 1: Add nginx Media Server (Recommended)

**Steps**:
1. Create `structa.cloud/compose/nginx/` directory
2. Copy nginx Dockerfile from ctc-research
3. Create nginx.conf for structa.cloud
4. Update docker-compose.yml to add `alliance-media` service
5. Configure Traefik labels for media routing

**Benefits**:
- Proper production setup
- Efficient static/media file serving
- Consistent with ctc-research architecture
- Better caching and performance

### Solution 2: Enable DEBUG Mode (Not Recommended)

**Steps**:
1. Set `DEBUG=true` in .env
2. Media files will be served by Django

**Drawbacks**:
- Security risk in production
- Poor performance
- Not a proper production setup
- Exposes debug information

### Solution 3: Use S3/CDN for Media (Future Enhancement)

**Steps**:
1. Configure AWS S3 or similar CDN
2. Update MEDIA_URL to point to CDN
3. Configure django-storages

**Benefits**:
- Scalable solution
- Better for distributed deployments
- Offloads media serving from application servers

---

## 8. Next Steps

1. ✅ **Task 2.1 Complete**: Diagnosis documented
2. ⏭️ **Task 2.2**: Update webpack configuration
3. ⏭️ **Task 2.3**: Fix static and media file serving (add nginx container)
4. ⏭️ **Task 2.4**: Implement asset health checks

---

## 9. Files Analyzed

### Configuration Files
- `structa.cloud/.env`
- `structa.cloud/docker-compose.yml`
- `structa.cloud/docker-compose.override.yml`
- `structa.cloud/configs/base/assets.py`
- `structa.cloud/configs/base/middlewares.py`
- `structa.cloud/alliance/urls.py`

### Webpack Files
- `structa.cloud/webpack/main.config.js`
- `structa.cloud/webpack/config.merged.js`
- `structa.cloud/assets/bundles/bundles.json`

### Comparison Files
- `ctc-research.com/docker-compose.yml`
- `ctc-research.com/compose/nginx/Dockerfile`
- `ctc-research.com/compose/nginx/nginx.conf`

### Library Files
- `libs/django-grep/src/django_grep/contrib/debug_tools/dev_urls.py`

---

## 10. Container Status

```
NAMES              STATUS                    PORTS
alliance-website   Up 12 minutes (healthy)   0.0.0.0:8280->5080/tcp
website            Up 6 minutes (healthy)
website-media      Up 12 minutes (healthy)   0.0.0.0:8271->80/tcp
```

**Observation**:
- `alliance-website` (structa.cloud) is healthy but has no media server
- `website-media` (ctc-research) exists and serves media files correctly

---

## Conclusion

The asset loading investigation is complete. Static files work correctly via WhiteNoise, but media files fail because there's no nginx media server container in the structa.cloud setup. The solution is to add an nginx container similar to the ctc-research architecture.

No 502 Bad Gateway errors were reproduced during testing. The actual issue is 404 Not Found for media files, which is expected behavior when media serving is not configured in production mode.
