# django-fusion — Webpack Enhancement Plan

> **Status:** Active
> **Owner:** django-fusion core team
> **Created:** 2026-08-10
> **Scope:** `libs/django-fusion/webpack/`, `projects/landing-fusion/`, `projects/precis/`
> **Depends on:** Existing webpack.config.js, workspace system, django-fusion-webpack-integration-plan.md

---

## 1. Executive Summary

django-fusion ships a Webpack 5 build system with:
- `webpack.config.js` — SCSS/JS asset bundling with MiniCssExtract + BundleTracker
- `webpack/workspace.config.js` — workspace loader (env-based: `FUSION_WEBPACK_WORKSPACE`)
- `webpack/workspaces/default.js` — default workspace entry points
- `FUSION_WEBPACK_WORKSPACE_PATH` — env var for custom workspace config file

This plan enhances the system so **projects can define their own webpack entries, output paths, and plugins** via Django settings (`FUSION_WEBPACK`) and environment variables — without forking the main `webpack.config.js`.

> **⚠️ Distributed Architecture (10 Aug 2026):** The legacy `projects/webpack/main.config.js` multi-site dispatcher has been **deprecated** in favor of per-project webpack configs. Each project now owns a full `webpack/<project>.config.js` that extends the shared `projects/webpack/base.config.js` factory. See §3.1 for the new structure.

---

## 2. Current State

### 2.1 What Works

| Feature | Status |
|---------|:------:|
| Webpack 5 build (SCSS → CSS, JS bundling) | ✅ |
| Workspace switching via `FUSION_WEBPACK_WORKSPACE` env | ✅ |
| Custom workspace file via `FUSION_WEBPACK_WORKSPACE_PATH` env | ✅ |
| `BundleTracker` → `webpack-stats.json` → `django-webpack-loader` | ✅ |
| Default SCSS entry: `src/django_fusion/assets/fusion.scss` | ✅ |
| Webpack validation management command (`webpack_validate`) | ✅ |

### 2.2 Gaps

| Gap | Impact |
|-----|--------|
| **No project-level SCSS/JS entry points** | Projects (landing-fusion, precis) must fork `webpack.config.js` to add their own entries. |
| **No `FUSION_WEBPACK` Django setting** | Projects cannot configure webpack from `settings.py` — must use env vars or workspace files. |
| **Workspace files must live in `libs/django-fusion/webpack/workspaces/`** | Or use `FUSION_WEBPACK_WORKSPACE_PATH` which is undocumented. No convention for project-owned workspace files. |
| **No `.env.example` for landing-fusion** | Missing from `projects/landing-fusion/` — no reference for webpack/fusion config. |
| **Precis `.env.example` is stale (ctc-research)** | References ctc-research domain, DB, and settings — not Precis-specific. |
| **No multi-project build command** | Each project must run its own `npm run build` in the django-fusion directory. |

---

## 3. Target Architecture

### 3.0 Two Complementary Webpack Systems

There are **two** webpack systems in this monorepo, serving different purposes:

| System | Location | Purpose | Template Tag |
|---|---|---|---|
| **django-fusion webpack** | `libs/django-fusion/webpack.config.js` | Builds django-fusion's own SCSS/JS component library | `{% render_bundle 'fusion' %}` |
| **Project webpack** | `projects/webpack/` + per-project configs | Builds project-specific assets (SCSS, JS, images) | `{% render_bundle 'main' %}` etc. |

Projects typically consume **both**: fusion component styles via the fusion bundle, and project-specific styles via their own bundle.

### 3.1 Distributed Project Structure (10 Aug 2026)

```
projects/webpack/                          ← Shared webpack foundation
├── base.config.js                         ← Factory: createConfig({name, entries, ...})
├── common.config.js                       ← Shared loaders, rules, plugins
├── paths.js                               ← resolvePaths(projectRoot) utility
├── postcss.config.js                      ← Shared PostCSS (overridable per project)
├── tailwind.config.js                     ← Shared Tailwind base (overridable per project)
├── package-copy.json                      ← Shared packages to copy
├── preload.js                             ← Package copy utility
├── main.config.js                         ← DEPRECATED (use per-project configs)
└── dev.config.js                          ← DEPRECATED (use per-project configs)

libs/django-fusion/
├── webpack.config.js          ← reads FUSION_WEBPACK from Django settings
│   ├── base entries (fusion)
│   ├── project entries (from FUSION_WEBPACK.ENTRIES)
│   ├── project output path (from FUSION_WEBPACK.OUTPUT_PATH)
│   └── project plugins (from FUSION_WEBPACK.PLUGINS)
│
├── webpack/
│   ├── workspace.config.js    ← already supports FUSION_WEBPACK_WORKSPACE_PATH
│   └── workspaces/
│       └── default.js         ← base workspace
│
projects/landing-fusion/
├── .env.example               ← NEW: webpack + fusion + project settings
├── backend/settings.py        ← defines FUSION_WEBPACK dict
└── webpack/                   ← Project-owned webpack
    ├── landing-fusion.config.js  ← NEW: extends projects/webpack/base.config.js
    └── landing.js                ← DEPRECATED (use landing-fusion.config.js)

projects/precis/
├── backend/.env.example       ← UPDATED: precis-specific settings
├── backend/settings.py        ← defines FUSION_WEBPACK dict
└── webpack/                   ← Project-owned webpack
    ├── precis.config.js          ← NEW: extends projects/webpack/base.config.js
    └── precis.js                 ← DEPRECATED (use precis.config.js)
```

### 3.2 How Projects Extend the Shared Base

```javascript
// projects/landing-fusion/webpack/landing-fusion.config.js
const createConfig = require('../../webpack/base.config');

module.exports = createConfig({
  name: 'landing-fusion',
  projectRoot: __dirname + '/..',
  entries: {
    landing: ['assets/static/styles/main.scss', 'assets/static/js/app.js'],
  },
  outputPath: 'backend/assets/static/bundles',
  aliases: {
    '@landing': 'assets/static',
    '@landing-styles': 'assets/static/styles',
  },
});
```

Build commands:
```bash
# Landing-Fusion
cd projects/landing-fusion
npx webpack --config webpack/landing-fusion.config.js --mode=production

# Precis LMS
cd projects/precis
npx webpack --config webpack/precis.config.js --mode=production
```

### 3.3 `FUSION_WEBPACK` Django Setting (for django-fusion webpack only)

```python
# In any project's settings.py
FUSION_WEBPACK = {
    "ENABLED": True,                         # Enable webpack build for this project
    "WORKSPACE": "landing",                  # Workspace name (maps to webpack/workspaces/<name>.js)
    "WORKSPACE_PATH": "/absolute/path/to/project/webpack/landing.js",  # Alt: direct path
    "ENTRIES": {                             # Additional entry points
        "landing": [
            "projects/landing-fusion/assets/static/styles/main.scss",
            "projects/landing-fusion/assets/static/js/app.js",
        ],
        # Entries are merged with the base "fusion" entry
    },
    "OUTPUT_PATH": "projects/landing-fusion/backend/assets/static/bundles/",
    "OUTPUT_PUBLIC_PATH": "/static/bundles/",
    "STATS_FILE": "projects/landing-fusion/backend/webpack-stats.json",
    "PLUGINS": [],                           # Additional webpack plugins (resolved by name)
    "SCSS_INCLUDE_PATHS": [                  # Additional sass-loader includePaths
        "projects/landing-fusion/assets/static/styles/",
    ],
    "ALIASES": {                             # Additional resolve.alias entries
        "@landing": "projects/landing-fusion/assets/static/",
    },
}
```

### 3.4 Build Commands

```bash
# django-fusion webpack (fusion component library):
cd libs/django-fusion
FUSION_WEBPACK_WORKSPACE=landing \
  FUSION_WEBPACK_WORKSPACE_PATH=../../projects/landing-fusion/webpack/landing-fusion.config.js \
  FUSION_PROJECT_ROOT=../../projects/landing-fusion \
  npx webpack --config webpack.config.js --mode production

# Project webpack (project-specific assets):
cd projects/landing-fusion
npx webpack --config webpack/landing-fusion.config.js --mode=production

cd projects/precis
npx webpack --config webpack/precis.config.js --mode=production

# Or via the Django management command (fusion webpack only):
cd projects/landing-fusion/backend
python manage.py webpack_validate --rebuild
# (reads FUSION_WEBPACK from settings and passes the correct env vars to webpack)
```

---

## 4. Implementation

### 4.1 Enhance `webpack.config.js`

Add project-level entry merging:

```javascript
// webpack.config.js — enhanced
const path = require("path");

// Read project overrides from FUSION_WEBPACK_* env vars (set by management command
// or Makefile from the project's Django settings).
const PROJECT_ENTRIES = process.env.FUSION_WEBPACK_ENTRIES
  ? JSON.parse(process.env.FUSION_WEBPACK_ENTRIES)
  : {};
const PROJECT_OUTPUT_PATH = process.env.FUSION_WEBPACK_OUTPUT_PATH || null;
const PROJECT_OUTPUT_PUBLIC = process.env.FUSION_WEBPACK_OUTPUT_PUBLIC || "/static/bundles/";
const PROJECT_STATS_FILE = process.env.FUSION_WEBPACK_STATS_FILE || null;
const PROJECT_SCSS_INCLUDES = process.env.FUSION_WEBPACK_SCSS_INCLUDES
  ? JSON.parse(process.env.FUSION_WEBPACK_SCSS_INCLUDES)
  : [];
const PROJECT_ALIASES = process.env.FUSION_WEBPACK_ALIASES
  ? JSON.parse(process.env.FUSION_WEBPACK_ALIASES)
  : {};

// ... (rest of existing config)

// Merged entries
const mergedEntries = {
  ...baseEntries,
  ...(workspace.entries || {}),
  ...PROJECT_ENTRIES,
};

// Merged output
const mergedOutput = {
  ...baseOutput,
  ...(workspace.output || {}),
  ...(PROJECT_OUTPUT_PATH ? { path: path.resolve(PROJECT_OUTPUT_PATH) } : {}),
  publicPath: PROJECT_OUTPUT_PUBLIC,
};

// Merged aliases
const mergedAliases = {
  "@fusion": path.resolve(SRC_DIR, "django_fusion/assets"),
  "@fusion-components": path.resolve(SRC_DIR, "django_fusion/comp"),
  ...PROJECT_ALIASES,
};

// Merged SCSS include paths
const sassOptions = {
  includePaths: [
    path.resolve(SRC_DIR, "django_fusion/assets"),
    ...PROJECT_SCSS_INCLUDES.map(p => path.resolve(p)),
  ],
  silenceDeprecations: ["import"],
};
```

### 4.2 Add `webpack_build` Management Command

Extend `webpack_validate` to pass project settings as env vars:

```python
# django_fusion/management/commands/webpack_build.py
class Command(BaseCommand):
    help = "Build webpack bundles for the current project."

    def handle(self, *args, **options):
        webpack_cfg = getattr(settings, "FUSION_WEBPACK", {}) or {}

        # Build env from Django settings
        env = os.environ.copy()
        if webpack_cfg.get("ENTRIES"):
            env["FUSION_WEBPACK_ENTRIES"] = json.dumps(webpack_cfg["ENTRIES"])
        if webpack_cfg.get("OUTPUT_PATH"):
            env["FUSION_WEBPACK_OUTPUT_PATH"] = webpack_cfg["OUTPUT_PATH"]
        if webpack_cfg.get("SCSS_INCLUDE_PATHS"):
            env["FUSION_WEBPACK_SCSS_INCLUDES"] = json.dumps(webpack_cfg["SCSS_INCLUDE_PATHS"])
        if webpack_cfg.get("ALIASES"):
            env["FUSION_WEBPACK_ALIASES"] = json.dumps(webpack_cfg["ALIASES"])

        # Run webpack from django-fusion root
        fusion_root = Path(django_fusion.__file__).parent.parent.parent
        subprocess.run(
            ["npx", "webpack", "--config", str(fusion_root / "webpack.config.js"),
             "--mode", "production"],
            cwd=str(fusion_root),
            env=env,
            check=True,
        )
```

### 4.3 Landing-Fusion `.env.example`

Create `projects/landing-fusion/.env.example` with all relevant settings.

### 4.4 Precis `.env.example` — Update

Replace the ctc-research-specific `.env.example` with Precis-specific settings.

---

## 5. Related Plans

| Plan | Path |
|---|---|
| Webpack Integration (Phase 1-2 done, Phase 3 planned) | [`django-fusion-webpack-integration-plan.md`](django-fusion-webpack-integration-plan.md) |
| django-fusion Tasks & MCP | [`django-fusion-tasks-mcp-plan.md`](django-fusion-tasks-mcp-plan.md) |
| Fusion Assets & Templates Cleanup | [`fusion-assets-templates-cleanup.md`](fusion-assets-templates-cleanup.md) |
| Landing-Fusion | [`../landing-fusion/README.md`](../landing-fusion/README.md) |
| Canonical Plan Registry | [`../README.md`](../README.md) |

---

*This plan is a living document. Update status as implementation progresses.*
