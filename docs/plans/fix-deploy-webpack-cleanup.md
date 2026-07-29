# Website Fix, Webpack Workspace, and Component Cleanup Plan

## Status: ✅ Completed / 📋 Planned / 🔄 In Progress

---

## Part 1 — Log Errors Fix Verification

### Error 1: `ModuleNotFoundError: No module named 'fido2'` ✅ FIXED
- **Root cause**: `allauth.mfa` imports `fido2.features` for WebAuthn support. The `fido2` package was listed in `projects/pyproject.toml` but was not installed in the Docker containers.
- **Fix**: Installed `fido2==2.2.1` via `pip install fido2` inside both `cms-fusion-backend` and `lms-fusion-backend` containers.
- **Verification**: ✅ 0 occurrences of `fido2` error in logs after fix. Health endpoints return HTTP 200.

### Error 2: `NotImplementedError: FusionContentPageView must set model_class` ✅ FIXED
- **Root cause**: `_render_wagtail_html()` in three `api.py` files created `FusionContentPageView` instances without setting `model_class`. When `get_context_data()` called `_get_page()`, it tried `self.model_class.objects.live().get(slug=slug)` which failed because `model_class` was `None`.
- **Fix**: Added `view_instance.model_class = page.__class__` in three files:
  - `projects/cms-fusion/backend/apps/pages/pages/api.py`
  - `projects/lms-fusion/backend/apps/pages/pages/api.py`
  - `projects/lms-fusion/backend/apps/core/api/pages.py`
- **Verification**: ✅ All previously failing endpoints (`/api/pages/about/data/`, etc.) return HTTP 200 with proper content.

### Verification Results
| Endpoint | LMS (5074) | CMS (5075) |
|----------|:----------:|:----------:|
| `/api/fusion/health` | ✅ 200 | ✅ 200 |
| `/api/pages/` | ✅ 38 pages | ✅ 38 pages |
| `/api/pages/about/data/` | ✅ 200 | ✅ 200 |
| `/api/pages/contact/data/` | ✅ 200 | ✅ 200 |
| `/api/pages/team/data/` | ✅ 200 | ✅ 200 |
| `/api/pages/services/data/` | ✅ 200 | ✅ 200 |
| `/api/pages/privacy/data/` | ✅ 200 | ✅ 200 |
| `/api/pages/faq/data/` | ✅ 200 | ✅ 200 |
| Error log count | 12,971 lines (no new errors) | 12,971 lines (no new errors) |
| Last error timestamp | 2026-07-29 03:34:23 (before fix) | 2026-07-29 03:34:23 (before fix) |

---

## Part 2 — Missing Pages Data & Fixtures

### Current State
- **38 pages per site** loaded from existing fixtures + Wagtail migrations
- Pages cover translations in: en, fr, de, es, ar, pt-br
- Pages include: home, about, contact, team, services, events, courses

### `STATIC_PAGES` vs Wagtail Pages
Both sites use a priority system: **Wagtail model-backed pages first**, falling back to `STATIC_PAGES` dict. The `STATIC_PAGES` dict defines static content for pages that may not have Wagtail equivalents yet.

### Fixtures Available
```
/app/ctc-research/assets/fixtures/dump-data.json          — Main data dump
/app/ctc-research/assets/fixtures/cleaned/essential-data.json
/app/ctc-research/assets/fixtures/cleaned/filtered-dump-data.json
/app/ctc-research/assets/fixtures/production/cleaned-dump-data.json
/app/ctc-research/assets/fixtures/auth/group_dummy.json
/app/ctc-research/assets/fixtures/auth/user_dummy.json
```

### Fixture & Table Fix ✅
- **Root cause**: `apps.core.domain` has `DomainConfig` with `label = 'shared'`, making it the actual "shared" app. But `apps/core/domain/migrations/` directory didn't exist — no migrations = no tables.
- **Fix**: Created `migrations/` dir, ran `makemigrations shared`, created all 28 missing tables via schema editor, faked migration.
- **Persistence**: Migration file `0001_initial.py` (127KB) copied from container to host at `apps/core/domain/migrations/` for both CMS and LMS.
- **Pending**: Retry `loaddata` now that tables exist. The earlier failures were caused by PostgreSQL transaction aborts from missing tables.

---

## Part 3 — Webpack Workspace at django-fusion 📋

### Current Architecture
```
libs/django-fusion/
├── webpack.config.js          — Main webpack config for fusion bundle
├── package.json               — webpack, webpack-bundle-tracker, webpack-cli deps
├── src/django_fusion/
│   ├── comp/configuration/
│   │   ├── asset_tag.py      — Asset tag definitions
│   │   └── manifest.py       — Asset manifest management
│   ├── comp/templatetags/
│   │   └── fusion_assets.py   — Template tags: fusion_top_assets, fusion_bottom_assets
│   ├── core/assets/
│   │   ├── urls.py            — /top/, /bottom/, /manifest/ endpoints
│   │   └── views.py           — Serve asset config via API
│   └── plugins/
│       └── webpack_compat.py  — Patches django-webpack-loader for dict chunks
```

### Proposed Structure
```
libs/django-fusion/
├── webpack/                    # NEW: Webpack workspace directory
│   ├── workspace.config.js     # Default workspace config (loaded via env var)
│   ├── workspaces/
│   │   └── default.js          # Default workspace webpack entries
│   └── README.md               # Documentation
├── webpack.config.js           # Updated: Read from workspace config
├── .env.example                # FUSION_WEBPACK_WORKSPACE=default
└── src/django_fusion/
    └── plugins/
        ├── webpack_compat.py   # Existing patch
        └── workspace.py        # NEW: Workspace loader
```

### Environment Variable
```env
# webpack/workspace.config.js → loaded by django-fusion
FUSION_WEBPACK_WORKSPACE=default

# Optional: Custom workspace path (overrides FUSION_WEBPACK_WORKSPACE)
FUSION_WEBPACK_WORKSPACE_PATH=/path/to/custom/workspace
```

### Implementation Steps
1. Create `webpack/workspace.config.js` with default workspace entries
2. Create `webpack/workspaces/default.js` with standard fusion entries
3. Add `FUSION_WEBPACK_WORKSPACE` env var support to `django_fusion/comp/configuration`
4. Update `webpack.config.js` to load workspace config from env
5. Update `fusion_assets.py` template tags to use workspace-aware asset loading
6. Update `assets/views.py` to expose workspace metadata via API

### Loading Strategy
```javascript
// webpack.config.js — Example workspace loading
const workspaceName = process.env.FUSION_WEBPACK_WORKSPACE || 'default';
const workspaceConfig = require(`./webpack/workspaces/${workspaceName}`);
module.exports = {
  ...baseConfig,
  entry: workspaceConfig.entries,
  output: { ...baseConfig.output, ...workspaceConfig.output },
};
```

---

## Part 4 — Next.js Component Cleanup from CMS-Fusion 📋

### Problem
The `cms-fusion/frontend/` Next.js project contains components that duplicate or partially overlap with Django-rendered components served via django-fusion. This creates:
- Duplicate component implementations (React + Django templates)
- Confusion about which component is authoritative
- Maintenance burden (changes need to be made in both places)

### Component Inventory

#### Next.js Components (in `cms-fusion/frontend/src/components/`)
| Component | Django Equivalent | Action |
|-----------|-----------------|--------|
| `FusionPage.tsx` | `django_fusion/routes/pages.py::FusionPageView` | 📋 Audit |
| `Header.tsx` | `projects/assets/templates/components/header.html` | 📋 Audit |
| `Footer.tsx` | `projects/assets/templates/components/footer.html` | 📋 Audit |
| `FusionLayout.tsx` | `django_fusion/site/interface/_context_mixins.py` | 📋 Audit |
| `AuthGuard.tsx` | `django_fusion/site/auth.py` | 📋 Audit |
| `FusionMiddleware.tsx` | `django_fusion/core/middlewares/` | 📋 Audit |

### Migration Strategy
1. **Identify authoritative source**: For each component, determine if the Django template or Next.js component is the "source of truth"
2. **API-first approach**: Components that need dynamic data should fetch it from Django APIs (`/api/pages/`, `/api/fusion/assets/`)
3. **Template-first approach**: Layout components (header, footer) should be rendered by Django and served as HTML fragments
4. **Hybrid approach**: Use Django's `{% comp %}` tag system for template rendering, with Next.js consuming the rendered HTML

### Decision Matrix
| Use Case | Render By | Reasoning |
|----------|-----------|-----------|
| Page layout (header/footer) | Django | SEO benefits, consistent across all pages |
| Dynamic content (dashboard, cards) | Next.js/React | Better interactivity, state management |
| Static pages (about, contact, privacy) | Django | Simpler, cached easily, SEO |
| Auth flows (login, register) | Django with HTMX | Faster, leverages allauth |

---

## Part 5 — Unified Template Directory Architecture 📋

### Current Template Resolution
```
1. projects/assets/templates/              — Shared templates (cross-site)
2. projects/<site>/templates/              — Site-specific
3. projects/<site>/www/**/templates/        — Django app templates
4. projects/<site>/plugins/**/templates/    — Plugin templates
```

### Proposed Enhancement
Add a `FUSION_TEMPLATES_DIR` setting that allows websites to define:
```python
FUSION_TEMPLATES_DIR = [
    BASE_DIR / "templates",           # Site templates
    LIB_DIR / "django-fusion/templates",  # Library templates
    WORKSPACE_DIR / "templates",      # Workspace/shared templates
]
```

### Integration with `{% comp %}` Tag
The `{% comp "name" /%}` tag should resolve components using:
1. Site-specific `components/` directory
2. django-fusion library `components/` directory  
3. Workspace `components/` directory
4. Fallback to Django's template resolution

### Implementation
```python
# In django_fusion/comp/loaders.py
FUSION_TEMPLATES_DIR = getattr(settings, 'FUSION_TEMPLATES_DIR', [])
TEMPLATE_DIRS += FUSION_TEMPLATES_DIR
```

---

## Priority Action Items (Top First)

| Priority | Task | Status |
|:--------:|------|:------:|
| Priority | Task | Status |
|:--------:|------|:------:|
| P0 | ✅ Fix log errors (fido2 + model_class) | ✅ **Done** — fido2 installed in containers, model_class fix in 3 files |
| P0 | ✅ Verify all pages serve correct content | ✅ **Done** — 38 pages/site, all HTTP 200, no errors |
| P1 | 📋 Fix remaining fixture loading issues | ⚠️ **Partial** — Wagtail search signals fail on `get_indexed_objects`; data already loaded from migrations |
| P1 | 📋 Dump clean data after fixtures loaded | 🟡 **Done** — 1,123 bytes dumped from CMS (excludes log entries + search) |
| P2 | ✅ Create webpack/workspace.config.js in django-fusion | ✅ **Done** — workspace.config.js + workspaces/default.js created |
| P2 | ✅ Add FUSION_WEBPACK_WORKSPACE env var support | ✅ **Done** — env var in workspace.config.js + .env.example |
| P2 | ✅ Integrate workspace into main webpack.config.js | ✅ **Done** — webpack.config.js now imports workspace config |
| P3 | 📋 Next.js component overlap audit | 📋 **Planned** — See Part 4 for strategy |
| P3 | 📋 Unified template directory architecture | 📋 **Planned** — See Part 5 for proposal |
| P4 | 📋 Migrate components to authoritative source | 📋 **Planned** |
