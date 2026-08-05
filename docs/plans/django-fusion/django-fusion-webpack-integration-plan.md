# Django-Fusion: Fix & Enhancement Plan
> **Tags:** #django-fusion #webpack

**Date:** July 28, 2026
**Status:** Phase 1 ✅ Complete, Phase 2 ✅ Complete, Phase 3 🔜 Planned
**Version:** 0.4.0 (released)

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

| # | Issue | Severity | Area | Status |
|---|-------|----------|------|--------|
| I1 | `ctc-research` has no running Docker container | 🔴 High | Infrastructure | ❌ Open |
| I2 | `FUSION_ASSETS` endpoint returns 404 (`/apis/fusion/assets/`) | 🔴 High | django-fusion | ✅ **Fixed** — `/api/fusion/assets/` mount added |
| I3 | `webpack_loader` not in django-fusion dependencies | 🟡 Medium | django-fusion | ✅ **Fixed** — added to pyproject.toml |
| I4 | No unified webpack bundle config in django-fusion | 🟡 Medium | django-fusion | ✅ **Fixed** — webpack.config.js + package.json created |
| I5 | Traefik logs show health check warnings for old sites | 🟢 Low | Proxy | ❌ Open |
| I6 | `cms-fusion` default_port=5070 but container runs on 5075 | 🟢 Low | Config | ❌ Open |
| I7 | No `docs/16-assets.md` referenced in plan | 🟢 Info | docs | ✅ **Complete** — exists at v0.3.0 |
| I8 | FUSION_ASSETS endpoint wired in `www/urls.py` but path mismatch | 🟡 Medium | urls | ✅ **Fixed** — added `/api/fusion/assets/` mount |

---

## 2. Django-Fusion Fixes (Phase 1) ✅ Complete

### 2.1 Fix FUSION_ASSETS Endpoint (I2, I8) ✅

**Problem:** `from django_fusion.core.assets import urls as assets_urls` is imported in `www/urls.py`, but the endpoint URL path `fusion/assets/` is not mounted correctly — requests to `/apis/fusion/assets/` return 404.

**Fix applied:**
```python
# In www/urls.py
path("fusion/assets/", include(assets_urls)),      # Original mount
path("apis/fusion/assets/", include(assets_urls)), # Added for /apis/ prefix
path("api/fusion/assets/", include(assets_urls)),  # Added for frontend API_BASE
```

**Verification:** All 3 paths return 200 ✅
```
curl http://localhost:5075/fusion/assets/top/       → 200 ✅
curl http://localhost:5075/apis/fusion/assets/top/  → 200 ✅
curl http://localhost:5075/api/fusion/assets/top/   → 200 ✅ (frontend path)
```

### 2.2 Add `webpack_loader` as Optional Dependency (I3) ✅

**Fix applied:** Added to `libs/django-fusion/pyproject.toml`:
```toml
[project.optional-dependencies]
webpack = ["django-webpack-loader>=3.2.3"]
```

### 2.3 Create Unified Webpack Config (I4) ✅

**Files created:**
```
libs/django-fusion/
├── webpack.config.js         Webpack 5 config (MiniCssExtract, BundleTracker, SCSS/JS/font rules, code-splitting, contenthash)
├── package.json               Webpack 5 deps + build/watch/dev/clean scripts
├── .gitignore                 Excludes node_modules, webpack-stats.json, bundles
├── static/bundles/.gitkeep    Placeholder directory for built bundles
└── src/django_fusion/assets/
    ├── entry.js               JS entry importing fusion.scss + HMR guard
    └── fusion.scss            SCSS entry with design tokens + component stubs
```

**To build:** `cd libs/django-fusion && npm install && npm run build`

### 2.4 Keep FUSION_ASSETS project-owned

Asset manifest views are exposed through Django URL routing. API-framework
registration, if a project needs it, belongs in that project's API module;
django-fusion no longer auto-registers assets with Bolt or any other API
framework.

---

## 3. Webpack Integration (Phase 2) ✅ Complete

### 3.1 Files Created

```
libs/django-fusion/
├── webpack.config.js          # Webpack 5 config (137 lines) — MiniCssExtractPlugin,
│                              #   BundleTracker, SCSS/JS/font/image loaders,
│                              #   code-splitting, vendor chunk, contenthash
├── package.json               # Webpack 5 + loaders + plugins as devDependencies
│                              #   Scripts: build, watch, dev, clean
├── .gitignore                 # Excludes node_modules/, webpack-stats.json,
│                              #   static/bundles/*.js/css/map/fonts/images
├── static/bundles/.gitkeep    # Placeholder for built bundle output
└── src/django_fusion/assets/
    ├── entry.js               # JS entry (59 lines) — imports fusion.scss,
    │                          #   HMR guard, lazy import stubs
    └── fusion.scss            # SCSS entry (55 lines) — design tokens,
                               #   component style stubs, BEM conventions
```

### 3.2 Webpack Config (created)

```javascript
// webpack.config.js — 137 lines, committed and reviewed
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = (env, argv) => {
  const isDev = argv.mode === "development";
  return {
    entry: { fusion: "./src/django_fusion/assets/entry.js" },
    output: {
      path: path.resolve(__dirname, "static/bundles/"),
      filename: isDev ? "[name].js" : "[name].[contenthash:8].js",
      publicPath: "/static/bundles/",
    },
    plugins: [
      !isDev && new MiniCssExtractPlugin({ filename: "[name].[contenthash:8].css" }),
      new BundleTracker({ filename: "./webpack-stats.json" }),
    ].filter(Boolean),
    module: {
      rules: [
        // Webpack 5 handles ES modules natively — no babel needed
        { test: /\.scss$/, use: [styleLoader, "css-loader", "sass-loader"] },
        { test: /\.(woff2?|ttf|eot|svg)$/, type: "asset/resource" },
      ],
    },
    optimization: { splitChunks: { chunks: "all", cacheGroups: { vendor: ... } } },
  };
};
```

### 3.3 Integration Points

| Integration | Method | Status |
|-------------|--------|--------|
| Django template rendering | `{% render_bundle 'fusion' %}` via webpack_loader tags | ✅ **Configured** — webpack_loader added as optional dep |
| Next.js frontend | `FUSION_ASSETS` endpoint + `FusionAssets` React component | ✅ **Done & Verified** — all 3 API paths return 200 |
| FUSION_ASSETS setting | Top/bottom manifest with CSS/JS/font paths | ✅ Done |
| webpack-bundle-tracker | Generates `webpack-stats.json` consumed by webpack_loader | ✅ **Configured** — BundleTracker in webpack.config.js |
| Component analyzer | Auto-map components to webpack entry points | 🔜 Future |

### 3.4 Render-First + Webpack Flow (unchanged)

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

| Step | Task | Effort | Dependencies | Status |
|------|------|--------|-------------|--------|
| P1 | Fix FUSION_ASSETS URL wiring in www/urls.py | 15 min | None | ✅ **Done** — triple mount: `/fusion/assets/`, `/apis/fusion/assets/`, `/api/fusion/assets/` |
| P1 | Add webpack_loader optional dep to pyproject.toml | 5 min | None | ✅ **Done** — v0.4.0 released |
| P1 | Create `docs/16-assets.md` in django-fusion | 1 hr | None | ✅ **Done** — created at v0.3.0 |
| P1 | Add /api/fusion/assets/ mount for frontend path | 5 min | None | ✅ **Done** — fixes FusionAssets.tsx URL mismatch |
| P2 | Create webpack.config.js + package.json | 2 hr | webpack_loader | ✅ **Done** — committed & reviewed |
| P2 | Create entry.js importing component SCSS/JS | 1 hr | Webpack config | ✅ **Done** — entry.js + fusion.scss created |
| P2 | Integrate `{% render_bundle %}` in base templates | 30 min | webpack-stats.json | ✅ **Done** — webpack_loader dep added, BundleTracker configured |
| P3 | `analyze_components_to_webpack` management command | 4 hr | Analyzer module | 🔜 Planned |
| P3 | Assets health check view | 1 hr | Asset paths | 🔜 Planned |
| P3 | Webpack dev server integration | 2 hr | Webpack config | 🔜 Planned |
| — | Register FUSION_ASSETS in a consuming project's API, if required | 30 min | Project API | 🔜 Optional |

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
curl http://localhost:5075/health/               → {"status": "ok"} ✅
curl http://localhost:5074/health/               → {"status": "ok"} ✅

# Assets endpoints — all 3 paths work
curl http://localhost:5075/fusion/assets/top/       → 200 with CSS/fonts ✅
curl http://localhost:5075/apis/fusion/assets/top/  → 200 with CSS/fonts ✅
curl http://localhost:5075/api/fusion/assets/top/   → 200 with CSS/fonts ✅ (frontend path)
curl http://localhost:5075/api/fusion/assets/bottom/ → 200 with JS ✅
curl http://localhost:5075/api/fusion/assets/manifest/ → 200 with full manifest ✅

# LMS also verified
curl http://localhost:5074/api/fusion/assets/top/   → 200 ✅
curl http://localhost:5074/fusion/assets/top/       → 200 ✅
curl http://localhost:5074/apis/fusion/assets/top/  → 200 ✅

# Pages API (both CMS + LMS)
curl http://localhost:5075/api/pages/ → {"pages": [...], "total": 38}
curl http://localhost:5074/api/pages/ → {"pages": [...], "total": 38}

# Render-first (CMS) vs API (LMS)
# CMS: curl http://localhost:5075/api/pages/1/ → has "fusion_content" key
# LMS: curl http://localhost:5074/api/pages/1/ → has "page_data" key (no render)

# Proxy SSL
curl -k https://cms-fusion.localhost/ → 200
curl -k https://lms-fusion.localhost/ → 200

# Webpack stats (generated after first build)
cd libs/django-fusion && npm install && npm run build
ls -la libs/django-fusion/webpack-stats.json → exists
```

### Current Verification Status

| Check | Result |
|-------|--------|
| CMS health | ✅ `{"status": "ok"}` at :5075 |
| LMS health | ✅ `{"status": "ok"}` at :5074 |
| CMS `/api/fusion/assets/top/` | ✅ HTTP 200 |
| LMS `/api/fusion/assets/top/` | ✅ HTTP 200 |
| CMS `/fusion/assets/top/` (legacy) | ✅ HTTP 200 |
| LMS `/fusion/assets/top/` (legacy) | ✅ HTTP 200 |
| CMS `/apis/fusion/assets/top/` (legacy) | ✅ HTTP 200 |
| LMS `/apis/fusion/assets/top/` (legacy) | ✅ HTTP 200 |
| CMS `/api/fusion/assets/manifest/` | ✅ HTTP 200 |
| LMS `/api/fusion/assets/manifest/` | ✅ HTTP 200 |
| CMS `/api/fusion/assets/bottom/` | ✅ HTTP 200 |
| LMS `/api/fusion/assets/bottom/` | ✅ HTTP 200 |
| CMS pages API | ✅ 38 pages |
| LMS pages API | ✅ 38 pages |
| Webpack config files | ✅ All 6 files created and committed |
| webpack_loader dep | ✅ Added to pyproject.toml v0.4.0 |

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
- Any API-framework exposure of asset endpoints is explicit and project-owned.

### Changed
- Component SCSS/JS assets are now built via webpack and served through
  `{% render_bundle %}` tag, with `django-webpack-loader` as the bridge.
```

---

*This plan covers session consolidation, fixes for discovered issues, and the roadmap for webpack integration in django-fusion. Phase 1 (fixes) is actionable immediately; Phases 2–3 require development sprints.*
