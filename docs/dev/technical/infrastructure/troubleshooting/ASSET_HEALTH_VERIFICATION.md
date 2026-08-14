# Asset Health Verification Guide
**Created**: June 2, 2026  
**Purpose**: Comprehensive asset loading verification from Django URLs

---

## Overview

This guide covers verification of all assets (CSS, JS, images, media) loaded through Django URLs. Uses django-fusion style testing to ensure:

- ✅ Static files properly collected
- ✅ Asset bundles built correctly
- ✅ URLs accessible from Django
- ✅ Template asset references valid
- ✅ Media server functional

---

## Quick Start

### Run Asset Health Verification

```bash
cd /root/site/websites
python tests/scripts/verify_assets_health.py
```

**Expected Output**:
```
🏥 ASSET HEALTH VERIFICATION SUITE
Django-Grep Style Verification

CTC Research (Port 5070)
────────────────────────
1️⃣  Django Application Health
✓ Django Health Check - Healthy

2️⃣  Static Files Collection  
✓ Static Files Collected - 1,684 files (125MB)

3️⃣  Asset Bundles
✓ Asset Bundles Built - 172 files (js=45, css=42, map=85)

4️⃣  Asset URLs Accessibility
✓ /static/css/main.css - HTTP 200
✓ /static/js/app.js - HTTP 200
✓ /static/images/logo.png - HTTP 200
✓ /media/ - HTTP 404 (OK)
✓ /assets/health/ - HTTP 200

5️⃣  Template Asset References (django-fusion)
✓ Static Tags - 150 references found
✓ Media URLs - 45 references found
✓ CSS Links - 85 references found
✓ JS Scripts - 120 references found

... (repeated for lms-demo and vresume)

📊 VERIFICATION SUMMARY

Site              Django     Static     Bundles    URLs       Templates
────────────────────────────────────────────────────────────────────────
CTC Research      ✓          ✓          ✓          ✓          157
LMS Demo          ✓          ✓          ✓          ✓          142
VResume           ✓          ✓          ✓          ✓          198

🎯 FINAL STATUS
✓ All asset health checks passed!
```

---

## Asset Health Tests

### 1. Django Application Health
**Tests**: Health endpoint accessibility  
**Command**: `curl http://localhost:5070/health/`  
**Expected**: HTTP 200 with healthy status

```bash
# Manual verification
for port in 5070 5071 5072; do
  echo "Port $port:"
  curl -s http://localhost:$port/health/ | head -3
done
```

### 2. Static Files Collection
**Tests**: Django's collectstatic output  
**Location**: `{site}/assets/staticfiles/`  
**Expected**: 1,684+ total files across all sites

```bash
# Manual verification
for site in ctc-research lms-demo VResume; do
  echo "$site:"
  find $site/assets/staticfiles -type f | wc -l
done
```

### 3. Asset Bundles Built
**Tests**: Webpack output bundles  
**Location**: `{site}/assets/bundles/`  
**Expected**: 661 total bundles (js, css, map files)

```bash
# Manual verification
for site in ctc-research lms-demo VResume; do
  echo "$site:"
  ls -1 $site/assets/bundles/*.{js,css} 2>/dev/null | wc -l
done
```

### 4. Asset URLs Accessibility
**Tests**: Direct HTTP requests to asset URLs  
**URLs Tested**:
- `/static/css/main.css` (200 = found)
- `/static/js/app.js` (200 = found)
- `/static/images/logo.png` (200/404 = OK)
- `/media/` (404 = OK, path routed)
- `/assets/health/` (200 = endpoint working)

```bash
# Manual verification
for port in 5070 5071 5072; do
  echo "Testing port $port:"
  curl -I http://localhost:$port/static/css/main.css
  curl -I http://localhost:$port/static/js/app.js
  curl -I http://localhost:$port/assets/health/
done
```

### 5. Template Asset References (django-fusion)
**Tests**: Template file scanning for asset tags  
**Types Scanned**:
- `{% static %}` tags
- `/media/` URLs
- `<link>` tags
- `<script>` tags

```bash
# Manual django-fusion style verification
for site in ctc-research lms-demo VResume; do
  echo "$site:"
  grep -r "{% static" $site/assets/templates | wc -l
  grep -r "/media/" $site/assets/templates | wc -l
  grep -r "<link" $site/assets/templates | wc -l
  grep -r "<script" $site/assets/templates | wc -l
done
```

---

## Asset File Structure

### Static Files (Collected by Django)
```
{site}/assets/staticfiles/
├── admin/                  # Django admin static files
├── css/                    # Compiled CSS
│   ├── main.css           # Main stylesheet
│   └── main.css.map       # Source map
├── js/                     # Bundled JavaScript
│   ├── app.js             # Main application JS
│   └── app.js.map         # Source map
├── images/                 # Static images
│   ├── logo.png
│   ├── favicon.ico
│   └── ...
├── fonts/                  # Web fonts
└── ...
```

### Asset Bundles (Webpack Output)
```
{site}/assets/bundles/
├── main.HASH.js           # Main JS bundle
├── main.HASH.css          # Main CSS bundle
├── main.HASH.js.map       # JS source map
├── main.HASH.css.map      # CSS source map
├── vendor.HASH.js         # Vendor dependencies
├── vendor.HASH.css        # Vendor styles
└── ...
```

### Media Files
```
assets/media/
├── avatar_images/         # User avatars
├── documents/             # Document uploads
├── images/                # Additional images
└── ...
```

---

## Asset Loading Flow

```
Django Request for Asset
│
├─ URL: /static/css/main.css
│
├─ 1. Django URL Router
│   └─ matches 'static' path
│
├─ 2. Django Static Files View
│   └─ looks in STATIC_ROOT (collected files)
│
├─ 3. File System Search
│   └─ finds in ctc-research/assets/staticfiles/css/main.css
│
├─ 4. HTTP Response
│   └─ serves file with proper headers
│
└─ 5. Browser Caching
    └─ caches with long expiration (1 year)

Media Request Flow
│
├─ URL: /media/uploads/image.jpg
│
├─ 1. Nginx (shared-proxy server)
│   └─ serves from /var/www/media/
│
├─ 2. File System Search
│   └─ finds in assets/media/uploads/image.jpg
│
└─ 3. HTTP Response
    └─ serves file with media type headers
```

---

## Django Asset Configuration

### Static Files Settings
```python
# Settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'assets' / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'assets' / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Media Files Settings
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'assets' / 'media'
```

### Whitenoise Configuration
```python
MIDDLEWARE = [
    # ...
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

# Compression and caching
WHITENOISE_AUTOREFRESH = False
WHITENOISE_COMPRESSION_QUALITY = 80
WHITENOISE_MAX_AGE = 31536000  # 1 year
```

---

## Common Issues & Solutions

### Issue: Static files not loading (404)
**Symptom**: CSS/JS files return 404 in browser console  
**Solution**:
```bash
# 1. Rebuild assets
npm --prefix assets run build:all

# 2. Collect static
docker exec web-ctc-research python manage.py collectstatic --noinput

# 3. Restart web server
docker compose restart web-ctc-research

# 4. Verify
python tests/scripts/verify_assets_health.py
```

### Issue: Media files not accessible
**Symptom**: Images/uploads return 404  
**Solution**:
```bash
# 1. Check media directory exists
ls -la assets/media/

# 2. Verify permissions
chmod 755 assets/media/

# 3. Restart shared-proxy container
docker compose restart shared-proxy

# 4. Verify
curl http://localhost/media/
```

### Issue: Template assets not rendering
**Symptom**: Assets in templates render as empty/broken links  
**Solution**:
```bash
# 1. Check static tag usage
grep -r "{% static" ctc-research/assets/templates

# 2. Load static in template
# At top of template: {% load static %}

# 3. Use correct syntax
# Correct: <img src="{% static 'images/logo.png' %}">
# Wrong: <img src="/static/images/logo.png">

# 4. Rebuild and collect
npm --prefix assets run build:all
docker exec web-ctc-research python manage.py collectstatic --noinput
```

### Issue: Source maps missing (dev)
**Symptom**: Browser can't find .map files for debugging  
**Solution**:
```bash
# Source maps are in bundles directory
ls -la ctc-research/assets/bundles/*.map

# Rebuild with source maps
npm --prefix assets run build

# Source maps auto-collected during collectstatic
```

---

## Verification Checklist

Before deployment, verify all items:

### Infrastructure ✓
- [ ] PostgreSQL healthy
- [ ] Redis healthy
- [ ] Traefik healthy
- [ ] shared-proxy healthy
- [ ] All web containers up

### Assets Built ✓
- [ ] npm packages installed
- [ ] webpack builds completed
- [ ] All 3 sites have bundles
- [ ] No build errors in logs

### Static Files ✓
- [ ] collectstatic ran successfully
- [ ] 1,684+ files in staticfiles
- [ ] All 3 sites staticfiles directory populated

### URLs Accessible ✓
- [ ] /static/css/main.css returns 200
- [ ] /static/js/app.js returns 200
- [ ] /media/ path accessible
- [ ] /assets/health/ returns 200

### Templates Valid ✓
- [ ] {% load static %} at top of templates
- [ ] {% static 'path' %} tags used correctly
- [ ] No hardcoded /static/ paths
- [ ] Media file references work

### Django Health ✓
- [ ] Health endpoint returns 200
- [ ] No errors in logs
- [ ] Database accessible
- [ ] Cache working

---

## Performance Optimization

### CSS/JS Compression
- Minified: ✓ (webpack production mode)
- Gzipped: ✓ (WhiteNoise compression)
- Source maps: ✓ (dev only)

### Image Optimization
```bash
# Check image sizes
du -sh assets/staticfiles/images/

# Optimize PNG
pngquant --quality=65-80 image.png

# Optimize JPG
jpegoptim --max=80 image.jpg
```

### Cache Headers
```
Static files: 1 year (31536000 seconds)
Media files: 30 days (2592000 seconds)
HTML: No cache (revalidate on each request)
```

---

## Automated Testing

### Run Complete Asset Verification
```bash
# Run all asset health checks
python tests/scripts/verify_assets_health.py

# Run with verbose output
python tests/scripts/verify_assets_health.py -v

# Run specific site only
python tests/scripts/verify_assets_health.py --site ctc-research
```

### Integration with CI/CD
```bash
# In deployment scripts
echo "Verifying assets..."
python tests/scripts/verify_assets_health.py || exit 1

echo "All asset checks passed! ✓"
```

---

## Next Steps After Verification

1. **✅ Verified Assets**: Proceed to deployment
2. **❌ Asset Failures**: Fix issues and re-verify
3. **📊 Generate Report**: Save verification output
4. **📝 Document**: Note any custom asset setup
5. **🔄 Monitor**: Watch logs in first 24 hours

---

## Reference Commands

```bash
# Complete asset rebuild & verification
make build-assets WEBSITE=ctc && \
docker exec web-ctc-research python manage.py collectstatic --noinput && \
python tests/scripts/verify_assets_health.py

# Check specific asset
curl -v http://localhost:5070/static/css/main.css

# Verify templates
grep -r "{% static" ctc-research/assets/templates | wc -l

# Check file sizes
du -sh ctc-research/assets/bundles/
du -sh ctc-research/assets/staticfiles/

# Monitor in real-time
watch -n 2 'curl -s http://localhost:5070/assets/health/ | jq .'
```

---

**Status**: ✅ Asset Verification System Ready  
**Script**: `/root/site/websites/tests/scripts/verify_assets_health.py`  
**Last Updated**: June 2, 2026
