# Django-Fusion: Fix & Enhancement Plan

**Date:** July 28, 2026
**Status:** Proposed
**Version:** 0.4.0 (target)

---

## 1. Current State Assessment

### 1.1 Infrastructure Status ✅

| Component | Status | Notes |
|-----------|--------|-------|
| CMS Backend (port 5075) | ✅ Healthy | 0 errors in logs, 38 pages loaded |
| LMS Backend (port 5074) | ✅ Healthy | 0 errors in logs, 38 pages loaded |
| CMS Frontend (port 3002) | ✅ Running | Next.js Docker |
| LMS Frontend (port 3001) | ✅ Running | Next.js Docker |
| Traefik Proxy | ✅ Healthy | SSL certs working, both sites 200 |
| Redis | ✅ Healthy | Cache layer |
| Postgres | ✅ Healthy | Database |

### 1.2 Architecture Status

| Aspect | CMS (cms-fusion) | LMS (lms-fusion) |
|--------|-----------------|-----------------|
| Render-First Default | `True` (component render) | `False` (API-first) |
| Pages Loaded | 38 (multi-language) | 38 (shared data) |
| Proxy SSL | ✅ 200 OK | ✅ 200 OK |
| FUSION_ASSETS configured | ✅ Top/bottom manifest | ✅ Top/bottom manifest |
| FusionAssets component | ✅ Created | ✅ Created |

### 1.3 Issues Found

| # | Issue | Severity | Area |
|---|-------|----------|------|
| I1 | `ctc-research` has no running Docker container | 🔴 High | Infrastructure |
| I2 | `FUSION_ASSETS` endpoint returns 404 (`/apis/fusion/assets/`) | 🔴 High | django-fusion |
| I3 | `webpack_loader` not in django-fusion dependencies | 🟡 Medium | django-fusion |
| I4 | No unified webpack bundle config in django-fusion | 🟡 Medium | django-fusion |
| I5 | Traefik logs show health check warnings for old sites | 🟢 Low | Proxy |
| I6 | `cms-fusion` default_port=5070 but container runs on 5075 | 🟢 Low | Config |
| I7 | No `docs/16-assets.md` referenced in plan | 🟢 Info | docs |
| I8 | FUSION_ASSETS endpoint wired in `www/urls.py` but path mismatch | 🟡 Medium | urls |

---

## 2. Django-Fusion Fixes (Phase 1)

### 2.1 Fix FUSION_ASSETS Endpoint (I2, I8)

**Problem:** `from django_fusion.core.assets import urls as assets_urls` is imported in `www/urls.py`, but the endpoint URL path `fusion/assets/` is not mounted correctly — requests to `/apis/fusion/assets/` return 404.

**Fix:**
```python
# In apps/core/urls.py or www/urls.py
from django_fusion.core.assets import urls as assets_urls

urlpatterns += [
    path("apis/fusion/assets/", include(assets_urls)),
]
```

**Verification:** `curl http://localhost:5075/apis/fusion/assets/top/` → 200 with JSON

### 2.2 Add `webpack_loader` as Optional Dependency (I3)

**Problem:** `django-webpack-loader` is not in `pyproject.toml` even though `django_fusion/plugins/webpack_compat.py` patches it.

**Fix:**
```toml
# In libs/django-fusion/pyproject.toml
[project.optional-dependencies]
webpack = ["django-webpack-loader>=3.2.3"]
```

### 2.3 Create Unified Webpack Config (I4)

**Problem:** No `webpack.config.js` or build pipeline at the django-fusion library level.

**Proposed structure:**
```
libs/django-fusion/
  webpack.config.js         ← Unified webpack config for component assets
  webpack-stats.json        ← Generated stats file (gitignored)
  src/django_fusion/assets/
    js/                     ← Shared JS entry points
    css/                    ← Shared CSS entry points  
    fonts/                  ← Shared font files
```

The webpack config would:
- Bundle Django component SCSS/JS into vendor chunks
- Output to `webpack-stats.json` consumed by `django-webpack-loader`
- Integrate with `FUSION_ASSETS` setting via the `{% render_bundle %}` tag

### 2.4 Wire FUSION_ASSETS into Bolt API Auto-Registration

**Problem:** The assets endpoints are not auto-registered in django-bolt's OpenAPI schema.

**Fix:** Register `GET /fusion/assets/top/`, `/bottom/`, `/manifest/` as Bolt API resources in `django_fusion/core/assets/loader.py` (new file).

---

## 3. Webpack Integration (Phase 2)

### 3.1 Files to Create

```
libs/django-fusion/
├── webpack.config.js          # Webpack 5 config for component assets
├── package.json               # Minimal package.json with webpack deps
├── src/django_fusion/
│   └── assets/
│       ├── entry.js           # Entrypoint: imports all component CSS/JS
│       └── components/        # Per-component CSS imports (auto-generated)
```

### 3.2 Webpack Config Overview

```javascript
// webpack.config.js
const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  entry: {
    fusion: "./src/django_fusion/assets/entry.js",
    // Per-component entries can be auto-generated from the manifest
  },
  output: {
    path: path.resolve(__dirname, "static/bundles/"),
    filename: "[name].[contenthash].js",
    publicPath: "/static/bundles/",
  },
  plugins: [
    new BundleTracker({ filename: "./webpack-stats.json" }),
  ],
  module: {
    rules: [
      { test: /\.css$/, use: ["style-loader", "css-loader"] },
      { test: /\.scss$/, use: ["style-loader", "css-loader", "sass-loader"] },
      { test: /\.(woff2?|ttf|eot|svg)$/, type: "asset/resource" },
    ],
  },
};
```

### 3.3 Integration Points

| Integration | Method | Status |
|-------------|--------|--------|
| Django template rendering | `{% render_bundle 'fusion' %}` via webpack_loader tags | Planned |
| Next.js frontend | `FUSION_ASSETS` endpoint + `FusionAssets` React component | ✅ Done |
| FUSION_ASSETS setting | Top/bottom manifest with CSS/JS/font paths | ✅ Done |
| webpack-bundle-tracker | Generates `webpack-stats.json` consumed by webpack_loader | Planned |
| Component analyzer | Auto-map components to webpack entry points | Future |

### 3.4 Render-First + Webpack Flow

```
CMS (Render-First):
  Django renders component HTML server-side
    ↓
  FUSION_ASSETS endpoint provides CSS/JS manifest
    ↓
  Next.js FusionAssets component injects <link>/<script> tags
    ↓
  webpack bundles component-specific SCSS/JS

LMS (API-First):
  Django serves page data via /api/pages/ endpoint
    ↓  
  Next.js renders components client-side
    ↓
  Same FUSION_ASSETS pipeline for CSS/JS loading
```

---

## 4. Phase 3: Enhancements

### 4.1 Component Analyzer ↔ Webpack Bridge

Create a Django management command `analyze_components_to_webpack` that:
1. Scans all registered components via the fragment analyzer
2. Maps each component to its SCSS/JS dependencies
3. Generates webpack entry points for each component
4. Updates `FUSION_ASSETS` to include component-specific bundles

### 4.2 Health Check for Assets

Add an `AssetsHealthView` that:
- Verifies `webpack-stats.json` exists and is valid JSON
- Checks that referenced bundles exist in the static directory
- Returns a health status for Docker/K8s probes

### 4.3 Webpack Dev Server for Development

Add a `webpack-dev-server` mode:
- Hot Module Replacement for Django/Wagtail template development
- Proxy config to route `/static/bundles/` to webpack-dev-server
- Toggle with `FUSION_WEBPACK_DEV=True` setting

---

## 5. Fix Rollout Schedule

| Step | Task | Effort | Dependencies |
|------|------|--------|-------------|
| P1 | Fix FUSION_ASSETS URL wiring in www/urls.py | 15 min | None |
| P1 | Add webpack_loader optional dep to pyproject.toml | 5 min | None |
| P1 | Create `docs/16-assets.md` in django-fusion | 1 hr | None |
| P2 | Create webpack.config.js + package.json | 2 hr | webpack_loader |
| P2 | Create entry.js importing component SCSS/JS | 1 hr | Webpack config |
| P2 | Integrate `{% render_bundle %}` in base templates | 30 min | webpack.stats.json |
| P3 | `analyze_components_to_webpack` management command | 4 hr | Analyzer module |
| P3 | Assets health check view | 1 hr | Asset paths |
| P3 | Webpack dev server integration | 2 hr | Webpack config |

---

## 6. ctc-research Status

| Check | Status |
|-------|--------|
| Docker container running | ❌ No container |
| Traefik routing | ⚠️ Returns 301 (redirect but no backend) |
| Fixtures loaded | ❌ Not running |
| Proxy config exists | ✅ `ctc-site-service` in Traefik config |

**Action needed:** Either:
- Restore `ctc-research` Docker stack and load fixtures
- Or remove stale Traefik config for `ctc-site-service` to clean up logs

---

## 7. Verification Checklist

After all phases, verify:

```bash
# Health endpoints
curl http://localhost:5075/health/               → {"status": "ok"}
curl http://localhost:5074/health/               → {"status": "ok"}

# Assets endpoints
curl http://localhost:5075/apis/fusion/assets/top/     → 200 with CSS/fonts
curl http://localhost:5075/apis/fusion/assets/bottom/  → 200 with JS
curl http://localhost:5075/apis/fusion/assets/manifest/ → 200 with full manifest

# Pages API (both CMS + LMS)
curl http://localhost:5075/api/pages/ → {"pages": [...], "total": 38}
curl http://localhost:5074/api/pages/ → {"pages": [...], "total": 38}

# Render-first (CMS) vs API (LMS)
# CMS: curl http://localhost:5075/api/pages/1/ → has "fusion_content" key
# LMS: curl http://localhost:5074/api/pages/1/ → has "page_data" key (no render)

# Proxy SSL
curl -k https://cms-fusion.localhost/ → 200
curl -k https://lms-fusion.localhost/ → 200

# Webpack stats
ls -la libs/django-fusion/webpack-stats.json → exists
```

---

## 8. Changelog Entry (proposed for django-fusion v0.4.0)

```markdown
## [0.4.0] — 2026-07-28

### Added
- Webpack 5 build config (`webpack.config.js`, `package.json`) for
  component asset bundling.
- `analyze_components_to_webpack` management command — maps registered
  fragments to webpack entry points.
- `webpack_loader` optional dependency (`pip install django-fusion[webpack]`).

### Fixed
- FUSION_ASSETS endpoint now correctly mounted at `/apis/fusion/assets/`
  with working top, bottom, and manifest endpoints.
- Bolt API auto-registration includes assets endpoints in OpenAPI schema.

### Changed
- Component SCSS/JS assets are now built via webpack and served through
  `{% render_bundle %}` tag, with `django-webpack-loader` as the bridge.
```

---

*This plan covers session consolidation, fixes for discovered issues, and the roadmap for webpack integration in django-fusion. Phase 1 (fixes) is actionable immediately; Phases 2–3 require development sprints.*
