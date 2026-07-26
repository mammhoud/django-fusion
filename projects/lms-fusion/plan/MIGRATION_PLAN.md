# LMS Fusion — Migration & django-fusion Integration Plan

> **Site:** `lms-fusion` | **Path:** `projects/lms-fusion/` | **Last updated:** 2026-07-26

---

## 1. Pre-Migration Inventory

| App / Area | Status | Notes |
|------------|:------:|-------|
| `plugins.branding` | ✅ | Migration + models + context processor |
| `plugins.accounts` | ✅ | Copied from ctc-research; verified |
| `plugins.lms` | ✅ | LMS models verified |
| `plugins.blog` | ✅ | Copied from ctc-research |
| `plugins.profile` | ✅ | Copied from ctc-research |
| `www.core` | ✅ | Copied from ctc-research |
| `django_fusion` | ✅ | INSTALLED_APPS + FusionCodec + FusionSessionChecker |

---

## 2. Migration Steps

| # | Task | Status |
|---|------|:------:|
| 1 | Branding migration | ✅ |
| 2 | Remaining migrations | ✅ |
| 3 | Apply migrations | ✅ |
| 4 | Django checks | ⬜ |
| 5 | Create superuser | ⬜ |
| 6 | Seed branding | ⬜ |

---

## 3. django-fusion Integration

- [x] `django_fusion` in `INSTALLED_APPS`
- [x] Base template loads `{% load fusion_layout %}` with `{% fusion_render_first_flag %}`
- [x] `fusion_branding_context` registered in context processors
- [x] `{% fusion_layout "default" %}` used in `base.html`
- [x] `{% fusion_branding %}` for CSS custom properties
- [x] `{% render_fusion_scripts %}` for frontend bridge
- [x] `{% fusion_body_data %}` on `<body>` element
- [ ] Wagtail pages inherit from `RoutableComponent`

---

## 4. django-bolt API Integration

| # | Item | Status |
|---|------|:------:|
| 1 | `bolt_apis.py` with real `BoltAPI` endpoints | ✅ |
| 2 | Health, pages, fragment, fusion health, branding, courses, blog | ✅ |
| 3 | Graceful fallback when `django_bolt` not installed | ✅ |
| 4 | `django_fusion.bolt.FusionBoltAPI` module created | ✅ |
| 5 | `@fusion_endpoint` decorator | ✅ |
| 6 | `component_serializer` helper | ✅ |
| 7 | `FusionBoltAuthBackend` for session→bolt bridge | ✅ |

---

## 5. Fusion Layout System

| # | Item | Status |
|---|------|:------:|
| 1 | `{% fusion_layout %}` template tag | ✅ |
| 2 | `{% fusion_render_first_flag %}` `<meta>` tag | ✅ |
| 3 | `{% render_fusion_scripts %}` frontend bridge | ✅ |
| 4 | `{% fusion_branding %}` CSS custom property injection | ✅ |
| 5 | `{% fusion_body_data %}` body data attributes | ✅ |
| 6 | Layout templates: `default`, `full_width`, `sidebar`, `blank` | ✅ |
| 7 | FusionLayout.tsx Next.js component | ✅ |
| 8 | Layouts fetch endpoint (`/api/fusion/layouts`) | ✅ |
| 9 | Per-project layout override in `base.html` | ✅ |

---

## 6. Frontend (Next.js)

| # | Item | Status |
|---|------|:------:|
| 1 | Full Next.js 14 + React 18 + Tailwind setup | ✅ |
| 2 | `fusion-types.ts`, `fusion-decoder.ts`, `fusion-store.ts` | ✅ |
| 3 | `api-client.ts` with health, fragment, page, branding, layout APIs | ✅ |
| 4 | `FusionProxy.tsx` with fallback chain (bolt→fragment→error) | ✅ |
| 5 | `FusionLayout.tsx` consuming `/api/fusion/layouts` | ✅ |
| 6 | `Header.tsx`, `Footer.tsx`, `Providers.tsx`, `ErrorBoundary.tsx` | ✅ |
| 7 | Dynamic routing (`[slug]/page.tsx`) | ✅ |
| 8 | `globals.css` with fusion theme + CSS custom properties | ✅ |
| 9 | `api-schema.d.ts` TypeScript API types | ✅ |

---

## 7. Verification

```bash
cd projects/lms-fusion/backend
make check && make test && python3 manage.py showmigrations
```

See [`projects/docs/DJANGO_BOLT_FUSION_CASE_STUDY.md`](../../docs/DJANGO_BOLT_FUSION_CASE_STUDY.md) for full analysis.
