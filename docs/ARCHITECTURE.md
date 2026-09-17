---
title: Architecture and data workflow
description: Request, component, task, asset, MCP, and documentation flows across Structa Cloud.
navigation:
  title: Architecture
  icon: i-lucide-landmark
object:
  type: "architecture"
  id: "docs.architecture"
attributes:
  source_path: "ARCHITECTURE.md"
  canonical_route: "/docs/en/architecture"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
tags:
  - structa-cloud
  - architecture
  - backend
  - frontend
  - infrastructure
  - docus
links:
  - label: "Project awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Project structure"
    to: "/project-structure"
    icon: "i-lucide-folder-tree"
---

# 🏗️ Structa Cloud — Architecture & Data Workflow

> Complete architecture reference: request lifecycle, component system, skeleton
> pipeline, background tasks, MCP integration, Docus documentation, and the full build chain.
> Updated: 18 August 2026

<!-- AI-generated: review needed -->

---

## 1. Request Lifecycle

Every HTTP request through a django-fusion project follows this path:

```
Client (Browser / Astro / HTMX / MCP)
  │
  ▼
┌─ Traefik / local dev server ──────────────────────────────────────┐
│  Routes by Host header → project container                        │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ Django WSGI/ASGI ────────────────────────────────────────────────┐
│  Middleware stack:                                                 │
│    SessionMiddleware → AuthMiddleware → SiteMiddleware →           │
│    CSRF → Locale → HTMX middleware → access control               │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ URL Routing ─────────────────────────────────────────────────────┐
│  urls.py → WagtailPage / ViewSet / API endpoint / Fragment route  │
└──────────────────────────────┬────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
        Wagtail Page     PageHandler       API/Fragment
        (CMS content)    (django-fusion)   (JSON/HTML)
              │                │                 │
              └────────────────┼─────────────────┘
                               │
                               ▼
┌─ Template Engine ─────────────────────────────────────────────────┐
│  {% comp "blocks/hero.html" /%}   ← django-fusion component tag  │
│  {% slot "title" /%}              ← content injection slots      │
│  {% fusion_page_skeleton ... %}   ← skeleton manifest embed      │
│  {% render_bundle 'main' %}       ← webpack asset injection      │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ Response ────────────────────────────────────────────────────────┐
│  Full page HTML / HTMX fragment / JSON / stream                   │
└────────────────────────────────────────────────────────────────────┘
```

### Dual Rendering (Precis Landing pattern)

Some projects use a **render-first / data-API** contract where a single endpoint may return
different formats:

| Header | Response | Consumed by |
|:-------|:---------|:------------|
| `Accept: text/html` (no `HX-Request`) | Full server-rendered HTML | Browser, Astro build |
| `HX-Request: true` | HTMX fragment | HTMX client swap |
| `Accept: application/json` | JSON payload | Astro `fetch()` in `onLoad` |
| `Accept: application/json` + `Fusion-Codec: v1` | Base64-encoded JSON via `FusionCodec` | TypeScript `FusionDecoder` |

---

## 2. Component System (`django_fusion.comp`)

### 2.1 Component Lifecycle

```
┌─ Template Author ─────────────────────────────────────────────────┐
│  Writes:  {% comp "blocks/hero.html" %}                           │
│           {% slot "title" %}Welcome{% endslot %}                  │
│           {% prop "variant" value="with-image" /%}                │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ comp tag library ────────────────────────────────────────────────┐
│  comp/tags/components/__init__.py  (formerly comp/templatetags/)  │
│  → resolves component path                                        │
│  → loads template from TEMPLATES_DIRS                             │
│  → renders with slots/props context                               │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ Component Registry ──────────────────────────────────────────────┐
│  comp/loader/templates.py                                         │
│  → autodiscovers *.html in registered template dirs               │
│  → maps component name → template path                            │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ Rendered HTML ───────────────────────────────────────────────────┐
│  <section class="hero hero--with-image" data-fusion-component>    │
│    <h1>Welcome</h1>                                               │
│    ...                                                             │
│  </section>                                                       │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Import Path Convention

Use the paths that exist in the checked-out framework. The component tag library
is currently owned by `django_fusion.comp.templatetags.components`; do not
invent a `comp.tags` alias in product code.

```python
# settings.py TEMPLATES — register the real library when needed:
TEMPLATES = [{
    "OPTIONS": {
        "builtins": [
            "django_fusion.comp.templatetags.components",
        ],
    },
}]
```

```django
{# Registered component usage #}
{% comp "blocks/hero.html" /%}
```

For routed backend views use canonical imports such as
`django_fusion.routes.components.routable.RoutableComponent` and
`django_fusion.routes.components.fragments.FragmentComponent`. Search the
library tree before relying on a historical import name.

---

## 3. Skeleton Pipeline (Phases 1–6)

The skeleton analyzer/resolver system bridges the Django backend and Astro frontend,
enabling **skeleton loading states** that match the actual component structure before
content arrives.

### 3.1 Pipeline Overview

```
┌─ Build Time ──────────────────────────────────────────────────────┐
│                                                                   │
│  python manage.py generate_skeleton_manifest                      │
│    ↓                                                              │
│  ┌─ SkeletonResolver ──────────────────────────────────────┐      │
│  │  1. scan(TEMPLATES_DIRS) → find template files           │      │
│  │  2. parse_template() → extract {% comp %} usages         │      │
│  │  3. resolve variant:                                     │      │
│  │     a. {# @skeleton: card #} comment (explicit)          │      │
│  │     b. data-skeleton-variant attribute                   │      │
│  │     c. filename heuristic (blocks/hero.html → hero)      │      │
│  │  4. to_json() → SkeletonEntry[]                          │      │
│  └──────────────────────────────────────┬──────────────────┘      │
│                                         ↓                          │
│  ┌─ ComponentAssetMap ─────────────────────────────────────┐      │
│  │  → reads webpack bundles.json                            │      │
│  │  → resolves "blocks/hero.html" → ["/static/hero.css"]    │      │
│  │  → enriches manifest with CSS/JS deps                    │      │
│  └──────────────────────────────────────┬──────────────────┘      │
│                                         ↓                          │
│  skeleton-manifest.json                                         │
│    → deployed as static asset                                   │
│    → consumed by Astro at build time                            │
└───────────────────────────────────────────────────────────────────┘

┌─ Runtime (Browser) ───────────────────────────────────────────────┐
│                                                                   │
│  1. Page loads → {% fusion_page_skeleton %} tag embeds manifest   │
│     <script>window.__FUSION_SKELETON_MANIFEST__ = {...}</script>  │
│                                                                   │
│  2. SkeletonBridge.astro initializes:                             │
│     ├─ FusionSkeletonBridge.renderAll()                           │
│     │   → renders 16 skeleton variant templates                   │
│     ├─ FusionComponentLoader.preloadCritical(top-3)               │
│     │   → <link rel="modulepreload">                              │
│     └─ FusionComponentLoader.observeComponents()                  │
│         → IntersectionObserver (200px margin)                     │
│                                                                   │
│  3. HTMX fragments arrive → htmx:afterSettle                      │
│     → skeletonBridge.swap(componentPath, realHTML)                │
│                                                                   │
│  4. window.__FUSION_PERF__  (RUM metrics)                         │
│     { skeletonCount, skeletonRenderMs, firstContentfulSkeletonMs }│
└───────────────────────────────────────────────────────────────────┘
```

### 3.2 Skeleton Variant Templates (16)

```
hero-section          stats-row            features-grid
testimonial           testimonials-carousel pricing-grid
faq-list              cta-banner           contact-form
timeline              team-grid            blog-grid
card                  line                 section-header
hero
```

### 3.3 API Endpoints

| Method | Path | Returns |
|:-------|:-----|:--------|
| `GET` | `/api/analyzer/analyze/` | Full template analysis (all pages, components) |
| `GET` | `/api/analyzer/skeleton/pages/home.html/` | Per-page skeleton manifest |
| `GET` | `/fusion/assets/components/` | Component→{css, js, vendor, preload} map |
| `GET` | `/fusion/assets/components/blocks/hero.html/` | Single component's assets |
| `GET` | `/fusion/assets/page/pages/home.html/` | Merged page asset set |

### 3.4 Settings

```python
# config/analyzer.py
FUSION_ANALYZER = {
    "ENABLED": True,
    "COMPONENT_TAG_NAME": "comp",
    "TEMPLATE_DIRS": None,  # auto-discovered from TEMPLATES
    "MAX_DEPTH": 10,
}

# config/skeleton.py
FUSION_SKELETON = {
    "ENABLED": True,
    "FIRST_PAINT_SKELETON": True,
    "HTMX_SKELETON": True,
    "ALLOWED_SKELETON_VARIANTS": [],
    "ANIMATION_DURATION": "1.4s",
    "REDUCED_MOTION_MODE": "prefers",
}

# config/assets.py
FUSION_COMPONENT_ASSETS = {
    "ENABLED": True,
    "PRELOAD_CRITICAL": True,
    "LAZY_LOAD_BELOW_FOLD": True,
    "CHUNK_SIZE_WARNING": 102400,
}
```

---

## 4. Background Tasks (`django_fusion.tasks`)

### 4.1 Architecture

```
┌─ Application Code ────────────────────────────────────────────────┐
│                                                                   │
│  from django_fusion.tasks import task                             │
│                                                                   │
│  @task(queue="email", max_retries=5)                              │
│  def send_welcome_email(user_id: int): ...                        │
│                                                                   │
│  # Enqueue                                                         │
│  send_welcome_email.send(user_id=42)                              │
│  send_welcome_email.delay(user_id=42)  # Celery-compat alias      │
│                                                                   │
│  # Run synchronously (tests / dev)                                │
│  send_welcome_email.run(user_id=42)                               │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
┌─ TaskRegistry ────────────────────────────────────────────────────┐
│  registry.py                                                      │
│  → autodiscover() scans INSTALLED_APPS for tasks.py modules       │
│  → register() stores TaskOptions per callable                     │
│  → send() delegates to configured backend                         │
│  → scheduled_tasks() returns cron-registered tasks                │
└──────────────────────────────┬────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                  ▼
    ┌─ InProcessBackend ───┐         ┌─ DramatiqBackend ──────┐
    │ (dev / no broker)    │         │ (production)            │
    │ → runs synchronously │         │ → Redis / RabbitMQ     │
    └──────────────────────┘         │ → retries, time limits │
                                     └────────────────────────┘
```

### 4.2 Activation

```python
# settings.py
FUSION_TASKS = {
    "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
    "BROKER_URL": "redis://localhost:6379/1",
}
# Without FUSION_TASKS → InProcessBackend (sync, safe for dev)
```

### 4.3 Celery Migration

| Before | After |
|:-------|:------|
| `from celery import shared_task` | `from django_fusion.tasks import task` |
| `@shared_task` | `@task(queue="default")` |

Celery is retired from the active runtime. Product workers use Dramatiq actors
under `backend/plugins/workers/`; the table above is a migration mapping only.
| `my_task.delay()` | `my_task.send()` or `.delay()` (compat alias) |
| `from sentry_sdk.integrations.celery import CeleryIntegration` | `try/except ImportError` — safe fallback |
| `dispatch_job(func)` | `@task` decorator + `.send()` |

### 4.4 Per-Project Task Modules

```
projects/
├── precis-landing/backend/apps/tasks/
│   ├── email_tasks.py      # send_newsletter, send_contact_form_notification
│   └── content_tasks.py    # warm_page_cache, generate_blog_preview_images
│
├── structa.cloud/backend/apps/tasks/
│   ├── email_tasks.py      # send_enrollment_confirmation, send_certificate
│   ├── course_tasks.py     # sync_course_completion_rates, send_weekly_digest
│   └── content_tasks.py    # process_uploaded_video, generate_ai_description
```

---

## 5. MCP Integration (Model Context Protocol)

### 5.1 Kilo MCP Server Router Map

The Kilo server (`.agents/mcp/mcp_server.py`) exposes django-fusion's
capabilities to AI agents via FastAPI endpoints:

```
Kilo MCP Server (port 8002)
├── /                           FusionMCPRouter
│   ├── GET  /fusion/info       → django-fusion version, viewsets, capabilities
│   ├── GET  /fusion/viewsets   → registered viewset listing
│   └── GET  /health/deps       → dependency availability check
│
├── /designer/                  DesignerMCPRouter
│   ├── GET  /designer/tools    → list 8 designer tools
│   ├── POST /designer/tools/call  → JSON-RPC: website_audit, form_scaffold, etc.
│   └── Auth: X-API-Key header (localhost bypass)
│
├── /tasks/                     TaskMCPRouter
│   ├── GET  /tasks/tools       → list 8 task tools
│   └── POST /tasks/call        → JSON-RPC: task.inspect, task.queues, etc.
│
└── /prompts/                   Prompt Catalog
    ├── GET  /prompts           → list all prompt metadata
    └── GET  /prompts/{id}      → single prompt detail
```

### 5.2 Task MCP Tools

| Tool | Description |
|:-----|:------------|
| `task.inspect` | Get task definition, queue, retry config |
| `task.queues` | List queues and their depth |
| `task.history` | Query task execution log (filter by status/name) |
| `task.retry` | Re-enqueue a failed task |
| `task.trigger` | Manually trigger a scheduled task |
| `task.stats` | Aggregate success/failure/latency stats |
| `task.purge` | Clear a queue (DANGER — confirmation required) |
| `task.workers` | Active worker count and status |

### 5.3 Designer MCP Tools

| Tool | Description |
|:-----|:------------|
| `website_audit` | Full template audit: components, blocks, assets |
| `webapp_enhancement_plan` | Feature recommendations for a project |
| `validate` | Validate component structure, missing templates |
| `form_scaffold` | Generate a django-fusion form component with fields |
| `table_scaffold` | Generate a django-fusion table component |
| `component_design` | Design a new component with slots/props |
| `field_rich_form` | Generate a form with rich field types |
| `field_rich_table` | Generate a table with rich column types |

### 5.4 MCP Directory Layout

```
.agents/mcp/
├── mcp_server.py            # FastAPI app — mounts all routers
├── config.json              # MCP server configuration
├── kilo.jsonc               # Kilo agent config
│
libs/django-fusion/src/django_fusion/
├── mcp/
│   ├── __init__.py
│   ├── fusion_router.py     # FusionMCPRouter
│   └── prompts.py           # Prompt catalog (generalized)
├── plugins/designer/
│   ├── mcp_router.py        # DesignerMCPRouter
│   └── tools.py             # Tool schemas + handlers
└── tasks/
    ├── mcp_router.py        # TaskMCPRouter
    └── mcp_handlers.py      # Tool handler implementations
```

---

## 6. Build Pipeline

### 6.1 Per-Project Asset Build

```
make build-assets
  ├─ ① make skeleton-manifest
  │   └─ python manage.py generate_skeleton_manifest
  │       --output assets/static/skeleton-manifest.json
  │       --page pages/home.html --page blog/index.html ...
  │
  └─ ② npx webpack --config webpack/<project>.config.js --mode=production
      ├─ Entry: assets/static/js/app.js, assets/static/styles/main.scss
      ├─ Output: assets/bundles/
      ├─ Plugins: BundleTracker → bundles.json
      └─ django-webpack-loader → {% render_bundle '<project>' %}
```

### 6.2 Webpack Configuration

```
projects/webpack/
├── base.config.js           # Shared: resolve, loaders, plugins
│   ├─ @<project> → project/assets/static/
│   ├─ @<project>-styles → project/assets/static/styles/
│   └─ @<project>-js → project/assets/static/js/
│
projects/precis/precis-landing/webpack/
└── precis-landing.config.js # Extends base, per-project entries/output
│
projects/structa.cloud/webpack/
└── precis.config.js         # Extends base, per-project entries/output
```

### 6.3 Full Build Chain (Precis Landing)

```
make build
  ├─ ① install-assets        → npm install
  ├─ ② skeleton-manifest     → generate_skeleton_manifest (DJANGO)
  ├─ ③ build-assets          → npx webpack (NPM)
  ├─ ④ css                   → tailwindcss → assets/static/css/fusion.css
  └─ ⑤ frontend build        → astro build → dist/
```

### 6.4 Full Build Chain (Precis LMS)

```
make build
  ├─ ① install-assets        → npm install
  ├─ ② skeleton-manifest     → generate_skeleton_manifest (DJANGO)
  ├─ ③ build-assets          → npx webpack (NPM)
  └─ ④ docker compose build  → Docker images
```

---

## 7. Data Flow Across Projects

### 7.1 Precis Landing — Marketing Site

```
┌─ Wagtail Admin ────────────────────────────────────────────────────┐
│  Editor creates/edits pages → StreamField blocks → Page publishes  │
└──────────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
┌─ Page Model ───────────────────────────────────────────────────────┐
│  HomePage, BlogPage, ProductPage, ...                             │
│  → get_context() adds fusion_render_first, site config             │
└──────────────────────────────────┬────────────────────────────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   ▼               ▼               ▼
           Full HTML        HTMX Fragment      JSON (Astro)
           (browser)        (partial swap)     (client fetch)
                   │               │               │
                   └───────────────┼───────────────┘
                                   │
                                   ▼
┌─ Template ─────────────────────────────────────────────────────────┐
│  {% comp "blocks/hero.html" /%}                                    │
│  {% fusion_page_skeleton template_path="pages/home.html" %}        │
│  {% render_bundle 'landing' %}                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 7.2 Precis LMS — Learning Platform

```
┌─ Student ──────────────────────────────────────────────────────────┐
│  Browses catalog → Enrolls → Watches lessons → Completes courses   │
└──────────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
┌─ Django Views ─────────────────────────────────────────────────────┐
│  CourseDetailView, LessonView, ProgressView, CertificateView       │
│  → renders Wagtail pages with learning context                     │
│  → tracks progress in CourseEnrollment / LessonProgress            │
└──────────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
┌─ Background Tasks ─────────────────────────────────────────────────┐
│  @task send_enrollment_confirmation(enrollment_id)                 │
│  @task sync_course_completion_rates()   [every 6h]                 │
│  @task send_weekly_learning_digest()    [Mon 09:00 UTC]            │
│  @task process_uploaded_video(video_id)                            │
└────────────────────────────────────────────────────────────────────┘
```

### 7.3 Formint POS — Desktop + Cloud Sync

```
┌─ Community Edition ────────────────────────────────────────────────┐
│  Tauri 2 + React 19 + Rust/Diesel + SQLite                         │
│  Offline-first — all data local                                    │
│  refund_sale(), useOfflineMode(), local-only operations            │
└────────────────────────────────────────────────────────────────────┘

┌─ Standard Edition ─────────────────────────────────────────────────┐
│  (Planned) Rust/Diesel-first + optional Django sidecar             │
│  Multi-currency, tax profiles, roles, CSV/JSON export              │
│  DataToken Shell → sync_queue table marks pending changes          │
│  Sidecar reconnect → flush pending to Django → DataToken tagging   │
└────────────────────────────────────────────────────────────────────┘

┌─ Professional Edition ─────────────────────────────────────────────┐
│  Django sidecar (required) + Astro 5 + Alpine/HTMX                 │
│  48 models, CRM, Unfold admin, django-fusion fragments             │
│  Channels WebSocket for multi-terminal sync                        │
│  Background tasks via @task                                        │
└────────────────────────────────────────────────────────────────────┘

┌─ Cloud Edition ────────────────────────────────────────────────────┐
│  Django multi-tenant + Channels ASGI                               │
│  Organization → Branch hierarchy                                   │
│  Async sync pipeline, backups, monitoring                          │
│  MCP tools for task management                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 8. Template & Static Asset Resolution

### 8.1 Template Discovery Order

Django's `TEMPLATES['DIRS']` and `APP_DIRS` combine to resolve templates.
django-fusion adds its own directories:

```
1. Project-level:    projects/<project>/backend/templates/
2. App-level:        projects/<project>/backend/apps/*/templates/
3. Shared assets:    projects/<project>/assets/templates/
4. django-fusion:    libs/django-fusion/src/django_fusion/templates/
5. Wagtail admin:    wagtail/admin/templates/
```

### 8.2 Static File Pipeline

```
Source                           → Build         → Collectstatic   → Served by
─────────────────────────────────────────────────────────────────────────────
assets/static/styles/*.scss      → webpack       → bundles/*.css   → Nginx/CDN
assets/static/js/*.js            → webpack       → bundles/*.js    → Nginx/CDN
assets/static/images/*           → (passthrough) → images/*        → Nginx/CDN
skeleton-manifest.json (generated) → (passthrough) → skeleton-*.json → Nginx/CDN
```

### 8.3 django-webpack-loader Contract

```python
# settings.py
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "assets/bundles/bundles.json"),
    }
}
```

```django
{# Template usage #}
{% load render_bundle from webpack_loader %}
{% render_bundle 'main' 'css' %}
{% render_bundle 'main' 'js' %}
```

---

## 9. Database Architecture

### 9.1 Production (PostgreSQL 16)

```
┌─ PostgreSQL Cluster ───────────────────────────────────────────────┐
│                                                                   │
│  Database per site:                                                │
│    precis_db       → Precis LMS (courses, enrollment, progress)    │
│    landing_db      → Precis Landing (Wagtail pages, blog)          │
│    syntara_db      → Syntara (chat conversations, templates)       │
│    formint_cloud   → Formint Cloud (organizations, sync, backups)  │
│                                                                   │
│  Shared worker queue: Redis (Dramatiq broker)                      │
│  Shared cache: Redis (sessions, skeleton cache, template cache)    │
└────────────────────────────────────────────────────────────────────┘
```

### 9.2 Development (SQLite)

```
projects/<project>/backend/db.sqlite3    # Per-project SQLite
:memory:                                  # Test suite (pytest + migrate --run-syncdb)
```

---

## 10. Docus Documentation Architecture

The documentation build follows the same source/build/runtime separation as the
application assets:

```text
docs/**/*.md or *.mdx  →  docs/scripts/prepare-content.mjs
                       →  docs/content/en/ (ignored, generated)
docs/ar-content/       →  docs/content/ar/ (ignored, generated)
                       →  Nuxt/Docus SSR server
                       →  shared-proxy + Traefik
                       →  docs.structa.cloud/ or media.structa.cloud/docs/
```

The preparation step enriches generated documents with Affine-style metadata:
`object` identity, `attributes`, `tags`, and `links`. Existing source frontmatter
remains authoritative. Never edit generated Docus content; update the source
Markdown or the preparation script instead.

## 11. Directory Map (Quick Reference)

```
structa.cloud/
├── docs/                     # Documentation (Docus + Nuxt Content)
│   └── plans/                # Plan registry (editions, pos, django-fusion, ...)
├── projects/                 # All product code
│   ├── precis/               # LMS — courses, enrollment, progress
│   ├── precis-landing/       # Marketing site — Astro + Wagtail
│   ├── syntara/              # AI Chat — Ollama, streaming
│   ├── formints/             # POS — 5 editions (Community → Cloud)
│   ├── configs/              # Shared Django settings
│   └── webpack/              # Shared webpack base config
├── libs/
│   └── django-fusion/        # Component system, tasks, MCP, skeleton
├── application/
│   ├── proxy/                # Traefik/Nginx/Caddy reverse proxy
│   ├── databases/            # PostgreSQL + Redis compose
│   └── agents/               # Kilo MCP server
├── tests/                    # Workspace integration tests
└── .agents/                  # AI agent skills
```

## Remarks & Notes

- This document describes shared boundaries; product-specific behavior belongs in the product documentation and nearest scoped `AGENTS.md`.
- The current filesystem map is `projects/structa.cloud/`, `projects/precis/precis-landing/`, and `projects/precis/precis-ctc/`; confirm aliases in `projects/Makefile` before using a legacy name.
- Docus metadata is generated from canonical Markdown by `docs/scripts/prepare-content.mjs`; generated content is not a second source.
