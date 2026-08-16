# django-fusion — Analyzer, Skeleton Loading & Asset API Enhancement Plan

> **Status:** Planned
> **Created:** 2026-08-10
> **Scope:** `libs/django-fusion/src/django_fusion/fragments/analyzer/`, `libs/django-fusion/src/django_fusion/config/assets.py`, `projects/precis/landi/`, `projects/precis/precis-lms/`
> **Depends on:** django-fusion-webpack-enhancement-plan.md (Webpack 5 base), django-fusion-tasks-mcp-plan.md (Dramatiq/MCP), django-fusion-enhancements.md (POS/sync)

---

## 1. Executive Summary

django-fusion already has:
- A **template/component analyzer** (`fragments/analyzer/`) that scans templates for `{% comp %}` usage, sections, and blocks, exposing them as JSON via `POST /api/analyzer/analyze/`.
- A **skeleton system** on both Django templates (`fusion/skeletons/default.html`, `pages/partials/skeleton.html`) and the Astro frontend (`Skeleton.astro` with 16 variants).
- An **asset pipeline** (`FUSION_ASSETS` setting, `fusion_top_assets`/`fusion_bottom_assets` template tags, `GET /fusion/assets/` API).

**The gap:** These three systems do not talk to each other. The analyzer knows which components exist on which pages but cannot tell the frontend what skeleton to show while a component loads. The skeleton system has 16 beautiful variants but they are hardcoded — the frontend cannot discover which variant matches which backend component on a given page. And the asset API returns a flat list of bundles, not per-component, on-demand chunks.

**This plan bridges all three** so that:
1. The analyzer learns to output **per-page ordered component lists with skeleton variant mappings**.
2. A new **dynamic skeleton resolver** (Python + JS) reads the analyzer manifest and renders the correct skeleton for every `{% comp %}` on every page.
3. The asset API exposes **per-component JS/CSS dependencies** (webpack-chunk mirroring), so the Astro frontend can load only the code needed for the visible components.
4. **Astro minimal JS** — a zero-config bridge that consumes the analyzer manifest, hydrates only in-viewport components, and shows skeleton placeholders with zero layout shift.

All features are **disabled by default** and enabled explicitly via Django settings (`FUSION_ANALYZER`, `FUSION_SKELETON`, `FUSION_COMPONENT_ASSETS`). The examples in this plan show the *recommended production values* once enabled, not the defaults.

---

## 2. Current State Assessment

### 2.1 Analyzer (`django_fusion/fragments/analyzer/`)

| Feature | Status | Gap |
|---------|:------:|-----|
| Template scanning (depth-capped) | ✅ | — |
| `{% comp %}` extraction → `CompUsage` | ✅ | — |
| Section markers (`@section:`, `data-section-id`) | ✅ | — |
| Per-page component tracking | ✅ (existing) | Props only, no skeleton info |
| Ordered component list | ✅ (existing) | Order is scan-order (DFS template traversal), not DOM-order |
| DOM-order resolution | ❌ | **Planned:** infer via `{% block %}` order in root template + optional `{# @order: N #}` markers |
| Skeleton variant classification | ❌ | **Not implemented** |
| Per-page skeleton manifest JSON | ❌ | **Not implemented** |
| Wagtail dynamic page support | ❌ | **Planned:** StreamField block→skeleton mapping via block type registry |

**Key file:** `django_fusion/fragments/analyzer/views.py` — `AnalyzeView.post()` produces `Page` objects with `components: [PageComponentUsage]`. The `Component` schema has `category` but no `skeleton` field.

### 2.2 Skeleton System

| Layer | File | Coverage |
|-------|------|----------|
| **Django skeleton template** | `libs/django-fusion/.../templates/fusion/skeletons/default.html` | Full-page first-paint skeleton (nav, hero, stats, features, testimonial, footer) |
| **Django partial** | `projects/precis/landi/backend/.../templates/pages/partials/skeleton.html` | Identical pattern, inline CSS, JS hide-on-DOM-ready |
| **Astro component** | `Skeleton.astro` (both precis-landing & precis) | 16 variants: `hero-section`, `stats-row`, `features-grid`, `testimonial`, `testimonials-carousel`, `pricing-grid`, `pricing-folded`, `faq-list`, `cta-banner`, `contact-form`, `section-header`, `hero`, `timeline`, `team-grid`, `blog-grid`, `card`, `line` |
| **CSS** | `globals.css` | `fusion-skeleton__*` BEM classes with shimmer animation |
| **LiveFragment** | `LiveFragment.astro` | Accepts `skeletonVariant` prop for HTMX in-flight placeholders |

**Gap:** The skeleton variants are **hand-mapped** — each Astro block component (`Hero.astro`, `Stats.astro`, `Features.astro`, etc.) imports `Skeleton.astro` and passes its own `variant` string. There is no automated way for a new component to declare its skeleton, and no way for the backend to tell the frontend "this page has a Hero, then Stats, then Features — show these three skeletons in order."

### 2.3 Asset Pipeline

| Feature | Status | Gap |
|---------|:------:|-----|
| `FUSION_ASSETS` Django setting (top/bottom CSS/JS) | ✅ | Flat list, not component-scoped |
| `{% fusion_top_assets %}` / `{% fusion_bottom_assets %}` | ✅ | — |
| `GET /fusion/assets/` API | ✅ | Returns flat manifest |
| `window.__FUSION_ASSETS__` JSON embed | ✅ | Same flat structure |
| Per-component asset mapping | ❌ | **Not implemented** |
| Webpack chunk → component lookup | ❌ | `webpack-bundle-tracker` writes `bundles.json` but no component→chunk map |
| `analyze_components_to_webpack` command | ✅ | Maps `{% comp %}` usage to SCSS/JS files — **exists but output is not consumed by any runtime system** |

**Key file:** `libs/django-fusion/src/django_fusion/management/commands/analyze_components_to_webpack.py` — already scans template `{% comp %}` usage and maps components to their SCSS/JS files, but the output is informational only (printed to stdout/CSV). It is not consumed by the asset API, the skeleton system, or the frontend.

### 2.4 Astro Frontend JS Loading

| Feature | Status | Gap |
|---------|:------:|-----|
| HTMX bootstrap | `lib/htmx-bootstrap.ts` | Eager-loads on every page |
| Fusion index | `src/fusion/index.ts` | Global `DOMContentLoaded` init |
| Per-page JS splitting | ❌ | All JS is in one bundle |
| Skeleton-to-component bridge | ❌ | Skeletons are manually placed in Astro templates |

---

## 3. Target Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DJANGO BACKEND                              │
│                                                                      │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐  │
│  │ FUSION_ANALYZER  │   │ FUSION_SKELETON   │   │FUSION_COMPONENT │  │
│  │ setting (opt-in) │   │ setting (opt-in)  │   │_ASSETS (opt-in) │  │
│  └────────┬─────────┘   └────────┬─────────┘   └────────┬────────┘  │
│           │                      │                       │           │
│  ┌────────▼─────────┐   ┌────────▼─────────┐   ┌────────▼─────────┐  │
│  │ Analyzer enhanced │   │SkeletonResolver  │   │ComponentAssetMap │  │
│  │ • skeleton field  │──▶│ • per-page JSON  │   │ • chunk→comp map │  │
│  │ • ordered comps   │   │ • fallback chain │   │ • lazy-load API  │  │
│  │ • variant mapping │   │ • SSG manifest   │   │ • bundles.json   │  │
│  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘  │
│           │                      │                       │           │
│  ┌────────▼──────────────────────▼───────────────────────▼─────────┐  │
│  │  GET /api/analyzer/skeleton/{page_path}/                        │  │
│  │  GET /api/assets/component/{component_name}/                     │  │
│  │  GET /fusion/assets/  (existing, enhanced with component maps)   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         ASTRO FRONTEND                                │
│                                                                       │
│  ┌─────────────────────┐   ┌─────────────────────────────────────┐   │
│  │ fusion-skeleton.ts   │   │ fusion-component-loader.ts          │   │
│  │ • reads skeleton     │   │ • reads component→chunk map         │   │
│  │   manifest           │   │ • dynamic import() per component     │   │
│  │ • renders matching   │   │ • IntersectionObserver hydration     │   │
│  │   skeletons          │   │ • HTMX afterSettle → swap skeleton  │   │
│  └─────────────────────┘   └─────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ <SkeletonBridge /> — single Astro component                    │    │
│  │ • Reads __FUSION_SKELETON_MANIFEST__ from backend             │    │
│  │ • Auto-renders skeletons for each component in page order      │    │
│  │ • Swaps skeletons → real content on HTMX settle or hydration   │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.1 Data Flow

1. **Build-time (or on-demand):** The analyzer scans all templates, produces a **skeleton manifest** JSON.
2. **Page request:** Django injects `window.__FUSION_SKELETON_MANIFEST__` containing the ordered component list for this page with skeleton variants.
3. **First paint:** `SkeletonBridge` (Astro or inline JS) renders the correct skeleton for each component.
4. **Hydration:** `fusion-component-loader.ts` dynamically imports only the JS chunks for the visible components.
5. **HTMX swaps:** After each fragment swap, the skeleton is automatically replaced with real content.

---

## 4. Phase 1 — Analyzer Enhancement (Skeleton Variant Classification)

### 4.1 Extend `Component` Schema with `skeleton` Field

```python
# django_fusion/fragments/analyzer/schemas.py

class Component(BaseModel):
    name: str
    path: str
    category: str = "UI"
    description: str = ""
    props: list[Prop] = Field(default_factory=list)
    slots: list[Slot] = Field(default_factory=list)
    # ── NEW ──
    skeleton: str | None = None          # variant name (e.g. "hero-section")
    skeleton_config: dict[str, Any] = Field(default_factory=dict)  # count, class, etc.
    dependencies: list[str] = Field(default_factory=list)  # JS/CSS deps
    load_priority: int = 0               # 0=eager, 1=viewport, 2=idle
```

### 4.2 Skeleton Variant Detection Strategy

The analyzer should detect which skeleton variant a component needs through three mechanisms, tried in order:

**Priority 1 — Explicit component metadata (new):**
```html
{# @skeleton: hero-section #}
{# @skeleton-config: {"count": 1, "class": "my-hero"} #}
{% comp "blocks/hero.html" / %}
```

**Priority 2 — Component file naming convention:**
Components in `blocks/` or `sections/` directories map to skeleton variants by name:
- `blocks/hero.html` → `hero-section`
- `sections/stats.html` → `stats-row`
- `components/features.html` → `features-grid`
- `blocks/testimonials.html` → `testimonials-carousel`
- `sections/pricing.html` → `pricing-grid`
- `blocks/faq.html` → `faq-list`
- `sections/cta.html` → `cta-banner`
- `blocks/contact.html` → `contact-form`
- `blocks/team.html` → `team-grid`
- `blocks/blog*.html` → `blog-grid`
- `blocks/timeline.html` → `timeline`

**Priority 3 — Category-based default:**
- `components/*` → `card`
- `layout/*` → `line`
- Otherwise → `line`

### 4.3 Per-Page Ordered Component Output

Enhance `AnalyzeView.post()` to emit pages with **DOM-ordered** components:

```python
# Enhanced Page schema
class Page(BaseModel):
    title: str
    path: str
    template: str | None = None
    sections: list[SectionInfo] = Field(default_factory=list)  # NEW
    components: list[PageComponentUsage] = Field(default_factory=list)

class SectionInfo(BaseModel):
    """A section in page DOM order with its components."""
    section_id: str
    section_name: str
    order: int
    components: list[PageComponentUsage] = Field(default_factory=list)
```

### 4.4 New Analyzer Endpoint: `GET /api/analyzer/skeleton/{page_path}/`

```python
# Returns the skeleton manifest for a specific page
{
  "status": "success",
  "page": {
    "title": "Home",
    "path": "pages/home.html",
    "skeleton_order": [
      {"variant": "hero-section", "props": {"count": 1}, "component": "blocks/hero.html"},
      {"variant": "stats-row",    "props": {"count": 4}, "component": "sections/stats.html"},
      {"variant": "features-grid","props": {"count": 6}, "component": "components/features.html"},
      {"variant": "cta-banner",   "props": {"count": 1}, "component": "sections/cta.html"}
    ]
  }
}
```

### 4.5 Settings — `FUSION_ANALYZER`

> **Default:** `FUSION_ANALYZER` is **not defined** by default — all analyzer features are off. The example below shows recommended production values once explicitly enabled.

```python
FUSION_ANALYZER = {
    "ENABLED": True,                          # Master switch (default: not present — disabled)
    "SKELETON_AUTO_DETECT": True,             # Priority 2 naming convention
    "SKELETON_DEFAULT_VARIANT": "line",       # Priority 3 fallback
    "EMIT_SKELETON_MANIFEST": True,           # Include skeleton data in analyzer output
    "SKELETON_MANIFEST_OUTPUT_PATH": None,    # Optional: write manifest.json to disk (for SSG)
    "CACHE_DURATION": 3600,                   # Cache skeleton manifests (seconds)
}
```

---

## 5. Phase 2 — Dynamic Skeleton Resolver

### 5.1 Python `SkeletonResolver`

```python
# django_fusion/fragments/skeleton/resolver.py

from dataclasses import dataclass, field
from typing import Any

@dataclass
class SkeletonEntry:
    variant: str
    component_path: str
    props: dict[str, Any] = field(default_factory=dict)
    order: int = 0

class SkeletonResolver:
    """Resolves which skeleton variant to show for each component on a page."""

    def __init__(self, analyzer_settings: dict | None = None):
        self.settings = analyzer_settings or {}

    def resolve_page_skeleton(self, page_path: str) -> list[SkeletonEntry]:
        """Return ordered skeleton entries for a page."""
        ...

    def resolve_component_skeleton(self, component_path: str) -> str:
        """Return the skeleton variant for a single component."""
        ...

    def to_json(self, entries: list[SkeletonEntry]) -> dict:
        """Serialize skeleton entries for frontend consumption."""
        ...
```

### 5.2 Backend Template Tag: `{% fusion_page_skeleton %}`

```django
{# In any page template that uses {% comp %} #}
{% load fusion_skeleton %}

<script>
  window.__FUSION_SKELETON_MANIFEST__ = {% fusion_page_skeleton template_path="pages/home.html" %};
</script>
```

The tag accepts `template_path` (the Django template path, e.g. `"pages/home.html"`), **not** a request URL path. For Wagtail pages, pass the page model's `get_template()` result. For static templates, pass the template name used in `TemplateView.template_name` or `{% extends %}`. The `SkeletonResolver` internally maps template paths to their analyzed component lists.

A convenience helper for views that don't know their template path:

```python
# In a ComponentViews subclass:
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["skeleton_manifest"] = SkeletonResolver().resolve_page_skeleton(
        self.template_name  # e.g. "fusion/layouts/landing.html"
    )
    return ctx
```

This tag calls `SkeletonResolver` internally and embeds the JSON directly in the page. Zero additional HTTP requests on first paint.

### 5.3 Settings — `FUSION_SKELETON`

> **Default:** `FUSION_SKELETON` is **not defined** by default — all skeleton features are off. Each project must opt in explicitly.

```python
FUSION_SKELETON = {
    "ENABLED": True,                          # (default: not present — disabled)
    "FIRST_PAINT_SKELETON": True,            # Show skeleton on full page loads
    "HTMX_SKELETON": True,                   # Show skeleton during HTMX fragment swaps
    "SKELETON_CSS_PATH": None,               # Custom skeleton CSS (default: built-in)
    "ALLOWED_SKELETON_VARIANTS": [           # Whitelist (empty = all allowed)
        "hero-section", "stats-row", "features-grid",
        "testimonial", "testimonials-carousel",
        "pricing-grid", "pricing-folded", "faq-list",
        "cta-banner", "contact-form", "section-header",
        "hero", "timeline", "team-grid", "blog-grid",
        "card", "line",
    ],
    "REDUCED_MOTION_MODE": "prefers",         # "prefers", "always", "never"
    "ANIMATION_DURATION": "1.4s",             # Shimmer cycle duration
}
```

---

## 6. Phase 3 — Component Asset APIs

### 6.1 `ComponentAssetMap` — Chunk → Component Lookup

```python
# django_fusion/core/assets/component_map.py

@dataclass
class ComponentAssetEntry:
    component_name: str
    css_deps: list[str]      # e.g. ["bundles/components.hero.css"]
    js_deps: list[str]       # e.g. ["bundles/components.hero.js"]
    vendor_deps: list[str]   # e.g. ["bundles/vendor.js"]
    size_bytes: int = 0
    preload: bool = False    # <link rel="modulepreload">

class ComponentAssetMap:
    """Maps components to their webpack chunks for lazy loading."""

    def __init__(self, bundles_path: Path, comp_manifest: dict):
        self.bundles = json.loads(bundles_path.read_text())
        self._build_lookup()

    def get_component_assets(self, component_name: str) -> ComponentAssetEntry | None:
        ...

    def get_page_assets(self, component_names: list[str]) -> dict[str, Any]:
        """Return the minimal set of JS/CSS chunks for a page's components."""
        ...

    def to_manifest(self) -> dict:
        """Serializable manifest for window.__FUSION_COMPONENT_ASSETS__."""
        ...
```

### 6.2 New API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/fusion/assets/components/` | Full component→chunk map |
| `GET` | `/fusion/assets/components/{name}/` | Single component's JS/CSS deps |
| `GET` | `/fusion/assets/page/{path}/` | Minimal chunk set for a page |
| `GET` | `/fusion/skeleton/page/{path}/` | Skeleton manifest for a page |

### 6.3 Template Tag: `{% fusion_component_assets %}`

```django
{% load fusion_assets %}

<script>
  window.__FUSION_COMPONENT_ASSETS__ = {% fusion_component_assets_json %};
</script>
```

### 6.4 Settings — `FUSION_COMPONENT_ASSETS`

> **Default:** `FUSION_COMPONENT_ASSETS` is **not defined** by default — per-component asset APIs are off. Enable explicitly for projects using lazy-loading.

```python
FUSION_COMPONENT_ASSETS = {
    "ENABLED": True,                          # (default: not present — disabled)
    "BUNDLES_JSON_PATH": "backend/assets/static/bundles/bundles.json",
    "COMPONENT_MANIFEST_PATH": "backend/assets/static/components/manifest.json",
    "PRELOAD_CRITICAL": True,               # Preload above-the-fold component chunks
    "LAZY_LOAD_BELOW_FOLD": True,           # Dynamic import() for below-fold
    "CHUNK_SIZE_WARNING": 100 * 1024,       # Warn if any chunk exceeds 100 KB
}
```

---

## 7. Phase 4 — Astro Frontend: Minimal JS

### 7.1 `fusion-skeleton.ts` — Dynamic Skeleton Bridge

```typescript
// libs/django-fusion/js/fusion-js/src/skeleton.ts

interface SkeletonEntry {
  variant: string;
  componentPath: string;
  props: Record<string, unknown>;
  order: number;
}

interface SkeletonManifest {
  page: { title: string; path: string };
  skeletons: SkeletonEntry[];
}

/**
 * Consumes __FUSION_SKELETON_MANIFEST__ and renders the correct
 * skeleton placeholder for each component in page order.
 */
export class FusionSkeletonBridge {
  constructor(private manifest: SkeletonManifest) {}

  /** Render all skeletons into their target containers. */
  renderAll(): void {
    for (const entry of this.manifest.skeletons) {
      const target = document.querySelector(`[data-fusion-skeleton="${entry.componentPath}"]`);
      if (target) {
        target.innerHTML = this.renderSkeleton(entry.variant, entry.props);
      }
    }
  }

  /** Swap a single skeleton with real content (called after HTMX settle). */
  swap(componentPath: string, html: string): void {
    const el = document.querySelector(`[data-fusion-skeleton="${componentPath}"]`);
    if (el) {
      el.outerHTML = html;
    }
  }

  private renderSkeleton(variant: string, props: Record<string, unknown>): string {
    // Matching the same BEM classes as Skeleton.astro & globals.css
    // ...
  }
}

// Auto-init from embedded manifest
if (window.__FUSION_SKELETON_MANIFEST__) {
  const bridge = new FusionSkeletonBridge(window.__FUSION_SKELETON_MANIFEST__);
  bridge.renderAll();
  window.__fusionSkeletonBridge = bridge; // expose for HTMX callbacks
}
```

### 7.2 `fusion-component-loader.ts` — On-Demand JS Loading

```typescript
// libs/django-fusion/js/fusion-js/src/component-loader.ts

interface ComponentAssetEntry {
  cssDeps: string[];
  jsDeps: string[];
  vendorDeps: string[];
  preload: boolean;
}

interface ComponentAssetMap {
  components: Record<string, ComponentAssetEntry>;
}

/**
 * Loads only the JS/CSS needed for the components visible on the current page.
 */
export class FusionComponentLoader {
  private loaded = new Set<string>();
  private observer: IntersectionObserver | null = null;

  constructor(private assetMap: ComponentAssetMap) {}

  /** Preload critical (above-fold) component chunks. */
  preloadCritical(pageComponents: string[]): void {
    for (const name of pageComponents) {
      const entry = this.assetMap.components[name];
      if (entry?.preload) {
        this.preloadChunk(entry);
      }
    }
  }

  /** Observe components and lazy-load their JS when they enter the viewport. */
  observeComponents(): void {
    this.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const name = (entry.target as HTMLElement).dataset.fusionComponent;
            if (name) this.loadComponent(name);
            this.observer!.unobserve(entry.target);
          }
        }
      },
      { rootMargin: '200px' }
    );
  }

  /** Dynamically import a component's JS. */
  async loadComponent(name: string): Promise<void> {
    if (this.loaded.has(name)) return;
    const deps = this.assetMap.components[name];
    if (!deps) return;
    this.loaded.add(name);

    // Load CSS
    for (const css of deps.cssDeps) {
      if (!document.querySelector(`link[href="${css}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = css;
        document.head.appendChild(link);
      }
    }

    // Dynamic JS import
    for (const js of deps.jsDeps) {
      await import(/* @vite-ignore */ js);
    }
  }

  private preloadChunk(entry: ComponentAssetEntry): void {
    for (const js of entry.jsDeps) {
      const link = document.createElement('link');
      link.rel = 'modulepreload';
      link.href = js;
      document.head.appendChild(link);
    }
  }
}
```

### 7.3 `SkeletonBridge.astro` — Single Astro Component

```astro
---
// components/ui/SkeletonBridge.astro
// Single Astro component that wires everything together.
// Drop it into any layout and it auto-renders skeletons + lazy-loads JS.
---
<script>
  import { FusionSkeletonBridge } from '@fusion-js/skeleton';
  import { FusionComponentLoader } from '@fusion-js/component-loader';

  // Skeleton manifest embedded by Django backend
  const skeletonBridge = new FusionSkeletonBridge(window.__FUSION_SKELETON_MANIFEST__ || { skeletons: [] });
  skeletonBridge.renderAll();

  // Component loader
  if (window.__FUSION_COMPONENT_ASSETS__) {
    const loader = new FusionComponentLoader(window.__FUSION_COMPONENT_ASSETS__);
    loader.preloadCritical(
      skeletonBridge.getManifest().skeletons.filter(s => s.order < 3).map(s => s.componentPath)
    );
    loader.observeComponents();
  }

  // HTMX integration: swap skeleton → real content on settle
  document.body.addEventListener('htmx:afterSettle', (e: Event) => {
    const target = e.detail?.target as HTMLElement;
    if (target) {
      const path = target.dataset.fusionSkeleton;
      if (path) skeletonBridge.swap(path, target.innerHTML);
    }
  });
</script>
```

### 7.4 Relationship with LiveFragment.astro

`LiveFragment.astro` already accepts a `skeletonVariant` prop and handles HTMX fragment loading with skeleton placeholders. `SkeletonBridge` does **not** replace it — they coexist at different layers:

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Full-page loads** | `SkeletonBridge.astro` | Renders skeleton for every `{% comp %}` on the page using the manifest, then swaps skeletons → real content as HTMX/Django delivers fragments |
| **Individual fragment swaps** | `LiveFragment.astro` | Shows a per-fragment skeleton inside its target container while waiting for the HTMX response |
| **Manual static skeletons** | `Skeleton.astro` (existing) | Used directly in Astro blocks — continues to work as before; gradually becomes an implementation detail consumed by `SkeletonBridge` and `LiveFragment` |

When both are active, the flow is:
1. Page loads → `SkeletonBridge` renders full-page skeleton wireframe
2. HTMX fragment request fires → `LiveFragment` swaps that region's skeleton to a variant-specific placeholder
3. HTMX response settles → `LiveFragment` swaps skeleton → real HTML
4. Remaining skeletons are progressively replaced as each fragment arrives

### 7.5 JS Module Paths

The new JS modules live under `libs/django-fusion/js/fusion-js/src/` and are published as the `@fusion-js` package:

```
libs/django-fusion/js/fusion-js/
├── package.json                   # name: "@fusion-js"
├── src/
│   ├── skeleton.ts                # FusionSkeletonBridge
│   ├── component-loader.ts        # FusionComponentLoader
│   └── index.ts                   # re-exports both
```

Projects import them as:

```typescript
import { FusionSkeletonBridge, FusionComponentLoader } from '@fusion-js';
```

Or individually for tree-shaking:

```typescript
import { FusionSkeletonBridge } from '@fusion-js/skeleton';
import { FusionComponentLoader } from '@fusion-js/component-loader';
```

### 7.6 Django Template Integration

```django
{# In base.html or any layout #}
{% load fusion_skeleton fusion_assets %}

<head>
  {% fusion_top_assets %}
  {% fusion_component_assets_json %}    {# window.__FUSION_COMPONENT_ASSETS__ #}
</head>
<body>
  {% fusion_page_skeleton template_path="pages/home.html" %}  {# window.__FUSION_SKELETON_MANIFEST__ #}

  {% block content %}{% endblock %}

  {% fusion_bottom_assets %}
</body>
```

---

## 8. Phase 5 — Build-Time Manifest Generation (SSG/CI)

### 8.1 Management Command: `generate_skeleton_manifest`

```bash
python manage.py generate_skeleton_manifest \
    --output backend/assets/static/skeleton-manifest.json \
    --page / \
    --page /blog/ \
    --page /pricing/
```

Produces a static JSON file that the Astro build can read at compile time:

```json
{
  "pages": {
    "/": {
      "title": "Home",
      "skeletons": [
        { "variant": "hero-section",   "component": "blocks/hero.html",  "order": 0 },
        { "variant": "stats-row",      "component": "sections/stats.html", "order": 1 },
        { "variant": "features-grid",  "component": "components/features.html", "order": 2 },
        { "variant": "cta-banner",     "component": "sections/cta.html", "order": 3 }
      ]
    }
  },
  "components": {
    "blocks/hero.html":       { "skeleton": "hero-section",   "css": ["bundles/hero.css"],    "js": ["bundles/hero.js"] },
    "sections/stats.html":    { "skeleton": "stats-row",      "css": ["bundles/stats.css"],   "js": [] },
    "components/features.html": { "skeleton": "features-grid","css": ["bundles/features.css"],"js": ["bundles/features.js"] },
    "sections/cta.html":      { "skeleton": "cta-banner",     "css": ["bundles/cta.css"],     "js": [] }
  }
}
```

### 8.2 Astro Build Integration

Rather than a custom Vite plugin (Astro/Vite already handles code-splitting via dynamic `import()` — which `FusionComponentLoader` uses), the build-time integration works as follows:

1. **`generate_skeleton_manifest` outputs `skeleton-manifest.json`** — a static JSON consumed by the Astro build.
2. **A Vite `virtual` module** (or plain JSON import) makes the manifest available at build time:
   ```typescript
   // src/lib/skeleton-manifest.ts
   import manifest from '@/generated/skeleton-manifest.json';
   export const skeletonManifest = manifest;
   ```
3. **Astro pages import the manifest** and use it to:
   - Preload critical component chunks via `<link rel="modulepreload">`
   - Generate static `<script type="application/json">` blocks for the page's skeleton order
   - Skip JS bundles for components that don't appear on the page

No custom Vite plugin is required — the manifest is a build artifact consumed as a regular JSON import. The existing `FusionComponentLoader` (Phase 4.2) handles runtime lazy-loading via dynamic `import()`.

---

## 9. Phase 6 — Performance & Observability

### 9.1 Skeleton Performance Metrics

```python
# django_fusion/fragments/skeleton/metrics.py

@dataclass
class SkeletonMetrics:
    """Collected by middleware for every page render."""
    page_path: str
    skeleton_count: int
    skeleton_render_ms: float
    first_contentful_skeleton_ms: float  # time to first skeleton DOM element
```

Expose via `window.__FUSION_PERF__` for Real User Monitoring (RUM).

### 9.2 Component-Level Cache Warming

Cache skeleton manifests in Redis to avoid filesystem scanning on every request:

```python
FUSION_SKELETON = {
    "CACHE_BACKEND": "redis",             # or "django", "filesystem"
    "CACHE_KEY_PREFIX": "fusion:skeleton:",
    "CACHE_TTL": 3600,
    "WARM_CACHE_ON_STARTUP": True,        # Pre-compute on worker start
}
```

### 9.3 Bundle Size Analysis

Enhance `analyze_components_to_webpack` to emit a **component-level bundle budget report**:

```
Component             CSS       JS        Total    Budget    Status
──────────────────────────────────────────────────────────────────
blocks/hero.html      4.2 KB    12.1 KB   16.3 KB  20 KB     ✅ OK
sections/stats.html   2.1 KB    0.5 KB    2.6 KB   10 KB     ✅ OK
components/features   8.7 KB    45.3 KB   54.0 KB  50 KB     ⚠️  OVER
```

---

## 10. Implementation Roadmap

| Phase | Deliverable | Effort | Dependencies |
|-------|-------------|:------:|--------------|
| **1.1** | Extend `Component`/`Page` schemas with `skeleton`, `skeleton_config`, `dependencies`, `load_priority` | Small | — |
| **1.2** | Skeleton variant detection (comments, naming convention, category fallback) | Medium | 1.1 |
| **1.3** | `GET /api/analyzer/skeleton/{page_path}/` endpoint | Small | 1.2 |
| **1.4** | `FUSION_ANALYZER` settings with tests | Small | 1.3 |
| **2.1** | `SkeletonResolver` Python class | Medium | 1.3 |
| **2.2** | `{% fusion_page_skeleton %}` template tag | Small | 2.1 |
| **2.3** | `FUSION_SKELETON` settings | Small | 2.2 |
| **3.1** | `ComponentAssetMap` class (chunk→component lookup) | Medium | 1.1 |
| **3.2** | `GET /fusion/assets/components/`, `GET /fusion/assets/components/{name}/`, `GET /fusion/assets/page/{path}/` | Small | 3.1 |
| **3.3** | `{% fusion_component_assets_json %}` template tag | Small | 3.2 |
| **3.4** | `FUSION_COMPONENT_ASSETS` settings | Small | 3.2 |
| **4.1** | `fusion-skeleton.ts` JS module | Medium | 2.3 |
| **4.2** | `fusion-component-loader.ts` JS module | Medium | 3.4 |
| **4.3** | `SkeletonBridge.astro` component | Small | 4.1, 4.2 |
| **4.4** | Django template integration (swaps, HTMX settle) | Small | 4.3 |
| **5.1** | `generate_skeleton_manifest` management command | Medium | 2.1, 3.1 |
| **5.2** | Vite plugin for Astro build-time consumption | Medium | 5.1 |
| **6.1** | Skeleton perf metrics + RUM | Small | 4.4 |
| **6.2** | Redis cache warming | Small | 5.1 |
| **6.3** | Component-level bundle budget report | Small | 3.1 |

**Total effort:** ~10 medium, ~12 small. Estimated 4-6 weeks for a single developer.

---

## 11. Recommended Additional Enhancements

### 11.1 Skeleton Designer (Wagtail Integration)

A Wagtail panel that shows a live preview of skeleton states for each page:

```python
# django_fusion/contrib/wagtail/skeleton_panel.py

class SkeletonPreviewPanel(Panel):
    """Shows the skeleton wireframe for the current page in the Wagtail editor."""
    ...
```

### 11.2 Component Health Dashboard

A Django admin dashboard that shows:
- Which components have skeletons defined vs. which are missing
- Bundle size per component over time
- Skeleton render performance trends

### 11.3 Skeleton A/B Testing

Toggle between skeleton variants and measure which one reduces perceived latency (via `window.__FUSION_PERF__`).

### 11.4 Automatic Skeleton Screenshot Generation

At build time, render each page with only skeletons and take a screenshot for documentation/design review.

### 11.5 Project-Specific Skeleton Overrides

Allow each project to override skeleton CSS and variants:

```python
# projects/precis/landi/backend/settings.py
FUSION_SKELETON = {
    "SKELETON_CSS_PATH": "landing_fusion/styles/skeletons.css",
    "SKELETON_TEMPLATE_DIR": "landing_fusion/skeletons/",
}
```

### 11.6 Webpack/Fusion Asset Parity Report

A CI check that ensures every CSS/JS chunk referenced in `FUSION_ASSETS` actually exists in `bundles.json`, and vice versa — preventing broken asset references.

---

## 12. Files Referenced

### django-fusion
- `libs/django-fusion/src/django_fusion/fragments/analyzer/schemas.py` — Pydantic schemas (to extend)
- `libs/django-fusion/src/django_fusion/fragments/analyzer/views.py` — `AnalyzeView` (to enhance)
- `libs/django-fusion/src/django_fusion/fragments/analyzer/parser.py` — `parse_template`, `CompUsage`
- `libs/django-fusion/src/django_fusion/fragments/analyzer/scanner.py` — `scan()`
- `libs/django-fusion/src/django_fusion/config/assets.py` — `AssetPipelineOptions`
- `libs/django-fusion/src/django_fusion/config/manifest.py` — `load_merged_asset_manifest()`
- `libs/django-fusion/src/django_fusion/core/assets/views.py` — `AssetsTopView`, `AssetsBottomView`, `AssetsManifestView`
- `libs/django-fusion/src/django_fusion/comp/templatetags/fusion_assets.py` — `fusion_top_assets`, `fusion_bottom_assets`, `fusion_assets_manifest`
- `libs/django-fusion/src/django_fusion/comp/loader/templates.py` — `find_components_in_template`, `NodeVisitor`
- `libs/django-fusion/src/django_fusion/comp/loader/discovery.py` — `discover_sections`
- `libs/django-fusion/src/django_fusion/templates/fusion/skeletons/default.html` — Django skeleton template
- `libs/django-fusion/src/django_fusion/management/commands/analyze_components_to_webpack.py` — Component→chunk mapping (to consume)
- `libs/django-fusion/js/fusion-js/` — JS package (new modules to add)

### Frontend
- `projects/precis/landi/frontend/src/components/ui/Skeleton.astro` — Astro skeleton component
- `projects/precis/landi/frontend/src/components/ui/LiveFragment.astro` — HTMX fragment with skeletonVariant
- `projects/precis/landi/frontend/src/styles/globals.css` — Skeleton CSS (`.fusion-skeleton__*`)
- `projects/precis/precis-lms/frontend/src/components/ui/Skeleton.astro` — Mirrored copy

### Backend
- `projects/precis/landi/backend/apps/pages/templates/pages/partials/skeleton.html` — Backend skeleton partial
- `projects/precis/landi/backend/settings.py` — `FUSION_ASSETS`
- `projects/precis/landi/backend/apps/pages/api.py` — `GET /fusion/assets/`

### Webpack
- `projects/webpack/base.config.js` — Webpack base factory
- `projects/precis/landi/webpack/precis-landing.config.js` — Project webpack config

---

## 13. Related Plans

| Plan | Path | Relationship |
|------|------|-------------|
| Webpack Enhancement | [`django-fusion-webpack-enhancement-plan.md`](django-fusion-webpack-enhancement-plan.md) | Webpack 5 base; chunk→component mapping depends on it |
| django-fusion Tasks & MCP | [`django-fusion-tasks-mcp-plan.md`](django-fusion-tasks-mcp-plan.md) | Background tasks for manifest generation |
| django-fusion Enhancements (POS) | [`django-fusion-enhancements.md`](django-fusion-enhancements.md) | Sync/fragment improvements; shared component infrastructure |
| Fusion Assets Cleanup | [`fusion-assets-templates-cleanup.md`](fusion-assets-templates-cleanup.md) | Asset consolidation prerequisite |
| Plan Registry | [`../README.md`](../README.md) | Canonical plan index |

---

*This plan is a living document. All features are opt-in via Django settings. Update status as implementation progresses.*
