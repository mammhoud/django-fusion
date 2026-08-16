# Architecture Notes

This document provides architectural hint notes for the monorepo structure.

## Monorepo Layout

The workspace root at `/data/coolify` contains:

- **Three site directories**: `precis-ctc/`, `lms-demo/`, `VResume/`
- **Shared `assets/` tree**: Contains frontend build configuration, npm packages, and shared code
- **`configs/` package**: Contains Django settings and configuration modules
- **`webpack/` directory**: Holds `common.config.js` and `main.config.js`
- **Flat `logs/` directory**: All three sites write to this location (currently no per-site isolation)

Each site directory follows the pattern `{site}/assets/static/js/app.js` as its Webpack entry point and `{site}/assets/bundles/{site}/` as its output directory.

## Shared vs Per-Site Frontend Packages

**Shared packages** (every site consumes these):
- Webpack 5, Babel, Sass, PostCSS, Tailwind CSS 4
- `mini-css-extract-plugin`, `webpack-bundle-tracker`
- Vue 3, Alpine.js, htmx.org, Bootstrap 5

**Per-site or optional packages**:
- ApexCharts, ECharts: Used by lms-demo and precis-ctc
- Chart.js: Lighter alternative available
- Grid.js: Data-table rendering
- Quill: Rich-text editing
- Swiper, GLightbox: Media-heavy pages
- FullCalendar: Only activated in lms-demo's scheduling views

Note: `axios` is not listed - HTTP requests use `fetch` or htmx's built-in request layer.

## Webpack Entry and Output Routing

`main.config.js` reads the `PROJECT_PATH`/`DJANGO_SITE`/`env.site` environment variable and resolves it through `SITE_DIR_MAP` to the canonical directory name:

- `ctc`, `ctc-research.com`, `ctc-website` → `precis-ctc`
- `structa`, `lms`, `lms-demo` → `lms-demo`
- `vresume`, `VResume`, `resume` → `VResume`

For precis-ctc and lms-demo, three entry points are emitted:
- `main`: Shared core
- `static`: CSS + vendor
- `app`: Site-specific

For VResume, only site-specific entry points are emitted.

## Stale `@theme` Alias

`main.config.js` declares `'@theme': path.resolve(workspaceRoot, 'assets/static/js/theme')`. The `assets/static/js/theme/` directory was deleted on June 2, 2026. Any import referencing `@theme` will silently resolve to a non-existent directory and fail at bundle time.

**Required fix**: Update the alias to point to `assets/static/js/modules` or remove entirely.

Similarly, `@layouts` and `@usecases` point into the deleted `theme/` subtree and must be redirected or removed.

## Python Settings Inheritance

Both precis-ctc and lms-demo resolve their Django settings through:
```python
from configs.settings import *
```
Then override `WEBSITE_NAME`, `WEBSITE_IDENTIFIER`, `SITE_ID`, and `ROOT_URLCONF`.

The `SILENCED_SYSTEM_CHECKS` list is duplicated verbatim in both `settings.py` files and should be consolidated into `configs/settings.py` to avoid drift.

VResume follows the same inheritance pattern.
