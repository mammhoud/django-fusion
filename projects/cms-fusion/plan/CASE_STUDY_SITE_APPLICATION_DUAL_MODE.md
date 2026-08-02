# Case Study — Enhancing Site & Application with Dual-Mode Rendering

> **Tags:** #cms-fusion #django-fusion #aha-stack #case-study #dual-mode  
> **Status:** 📋 Case Study  
> **Related:** [ASTRO_MIGRATION_PLAN.md](./ASTRO_MIGRATION_PLAN.md)

---

## 1. Problem

When migrating the cms-fusion frontend from Next.js to the **AHA stack** (Astro + HTMX + Alpine.js), the `fusion_render_first` contract needs to work at **every** rendering layer — not just Wagtail pages:

1. **HTMX fragment components** (course grid, blog list, dashboard KPIs) currently render HTML unconditionally. There is no data-mode equivalent for clients that want JSON.
2. **RoutableComponent full-page views** (dashboard) render HTML templates but expose no data serialization.
3. **Site chrome** (header / footer / navigation) is Django-template only. A data-mode client has no way to receive the Site's navigation structure.
4. **Language, session preference, and Wagtail page context** are not surfaced in data responses.

---

## 2. Solution — `FusionDualModeMixin`

A single mixin, added to **django-fusion** so every fusion project benefits:

```
django_fusion/routes/dual_mode.py
└── FusionDualModeMixin
    ├── get_effective_render_first(request)   # session → component → setting
    ├── get_fragment_data()                    # JSON-serialisable payload
    ├── get_data_meta()                        # component identity + site nav
    ├── get_site_context()                     # walk parents → Site navigation
    └── dispatch()                             # route HTML vs data mode
```

### 2.1 The render-first decision

```python
def get_effective_render_first(self, request):
    if self.force_render_first:
        return True                       # hard override to HTML (head-content)
    if self.force_data_mode:
        return False                      # hard override to data
    header = request.headers.get("X-Fusion-Render-First")
    if header in ("true", "false"):
        return header == "true"           # per-request override
    if request and hasattr(request, "session"):
        return bool(get_session_render_first(request))   # session wins
    return bool(self.get_fusion_render_first())          # component / setting
```

**Priority chain** (mirrors `FusionSessionChecker` + `bolt/decorators.py`):

1. `force_render_first` — HTML-only components (e.g. head-content)
2. `force_data_mode` — data-only components
3. `X-Fusion-Render-First` header — per-request override (data clients)
4. Session preference — `request.session['fusion_render_first']` (7-day expiry)
5. Component attribute / `COMPONENTS.FUSION_RENDER_FIRST_DEFAULT` setting

This is exactly the same chain the Next.js `FusionDecoder` used — but now
enforced server-side by Django.

### 2.2 HTML mode (render-first = True)

The parent pipeline is untouched: `FragmentComponent` renders its fragment
template, `RoutableComponent` renders its full-page template. SEO-friendly,
zero client-side JS for that region.

### 2.3 Data mode (render-first = False)

`dispatch()` short-circuits to `render_data_response()`:

```python
{
  "status": 200,
  "message": "Success",
  "data": {
    "encoded": "fusion_v1:<base64>",      # FusionCodec.encode(get_fragment_data())
    "meta": {
      "component": "CourseGridFragment",
      "fragment_name": "htmx.course_grid",
      "fusion_render_first": False,
      "language": "en",                    # ← language integration
      "site": {                            # ← Site encapsulation
        "title": "Fusion CMS",
        "navigation": [ { "type": "application", "title": "Learning", ... } ],
        "active_app": "Learning"
      }
    }
  }
}
```

The client decodes `data.encoded` with the existing TypeScript
`FusionDecoder` and renders the content; the `meta.site.navigation` block
lets it draw the header/footer chrome around the content.

---

## 3. Enhancing `Site` & `Application`

`get_site_context()` walks the viewset parent chain:

```
component.parent → Application (LMSApp) → Site (Fusion CMS)
```

For the first `Application` it records `active_app` and enumerates
`site.menu_items()`:

| Type | Serialized shape |
|------|------------------|
| `Application` child | `{type, title, icon, app_name, active, menu_items[]}` |
| `menu_path` item | `{type, title, icon, name}` |

This gives data-mode clients the **same navigation tree** the Django
`side-nav/app_menu.html` template renders — no duplication.

### Example — LMS Dashboard

```python
class DashboardComponent(FusionDualModeMixin, RoutableComponent):
    route_path = "dashboard/"
    template_name = "lms/dashboard.html"

    def get_fragment_data(self):
        return {
            "stats": self._get_stats(),
            "recent_enrollments": list(
                self._get_recent_enrollments().values("id", "course__title", "student__username")
            ),
        }
```

* HTML mode  → `lms/dashboard.html` rendered server-side
* Data mode  → stats + recent enrollments as JSON, plus Site navigation

### Example — Course grid fragment

```python
class CourseGridFragment(HTMXFragmentMixin, FusionDualModeMixin, FragmentComponent):
    route_name = "htmx-course-grid"
    route_path = "courses/grid/"
    fragment_name = "htmx.course_grid"

    def get_fragment_data(self):
        return {"courses": [...], "pagination": {...}, "q": ...}
```

---

## 4. Integrations

### 4.1 Language (`django.utils.translation.get_language`)

`get_data_meta()` includes `"language": get_language()` so the data-mode
client knows the active locale. The `DefaultLanguageMiddleware` already
persists the choice via cookie / `?lang=` query param, so the fragment
request carries the language forward automatically.

### 4.2 Session (`FusionSessionChecker`)

`get_effective_render_first()` delegates to `get_session_render_first()`
which caches the preference in `request.session['fusion_render_first']`
(7-day expiry). Users toggling rendering mode get a consistent experience
across HTMX fragments and routable views.

### 4.3 Wagtail pages

`FusionPageView` already resolves `fusion_render_first` per-page. A
`FusionDualModeMixin` subclass combined with `FusionPageView` gives:

* HTML mode → the page's Wagtail-rendered template
* Data mode → the page's serialized content (hero, body, children) as JSON,
  wrapped with Site navigation

```python
class FusionPageDualModeView(FusionDualModeMixin, FusionPageView):
    def get_fragment_data(self):
        page = self._get_page()
        return {
            "slug": page.slug, "title": page.title,
            "layout": page.effective_layout,
            "hero_heading": getattr(page, "hero_heading", ""),
            "body": getattr(page, "body", ""),
            "children": [...],
        }
```

---

## 5. Client-side usage (AHA stack)

```astro
---
// Astro page — server-side fetch
const BACKEND = "http://backend:5075";
const res = await fetch(`${BACKEND}/api/htmx/courses/grid/`, {
  headers: { "X-Fusion-Render-First": "false" },   // ask for data mode
});
const { data } = await res.json();
const page = FusionDecoder.decode(data.encoded);    // existing TS decoder
const { site, language } = data.meta;               // navigation + locale
---
<!-- Site chrome drawn from meta.site.navigation -->
<SiteNav items={site.navigation} />

<!-- Content rendered from decoded data -->
<section>
  {page.courses.map(course => <CourseCard course={course} />)}
</section>
```

HTMX fragments can also opt-in per request by sending
`X-Fusion-Render-First: false` — the session preference is overridden for
that single request.

---

## 6. File map

| File | Change |
|------|--------|
| `libs/django-fusion/src/django_fusion/routes/dual_mode.py` | **New** — `FusionDualModeMixin` |
| `libs/django-fusion/src/django_fusion/routes/__init__.py` | Export `FusionDualModeMixin` |
| `projects/cms-fusion/backend/apps/core/htmx/components.py` | 5 components now dual-mode |
| `projects/cms-fusion/backend/apps/pages/lms/components.py` | `DashboardComponent` dual-mode |
| `projects/cms-fusion/backend/apps/pages/blog/components.py` | `BlogPostListFragment` dual-mode |

---

## 7. Test matrix

| Scenario | Expected |
|----------|----------|
| `fusion_render_first=True` + HTMX request | HTML fragment + `HX-Partial: true` |
| `fusion_render_first=False` + HTMX request | JSON `{status, message, data:{encoded, meta}}` |
| `fusion_render_first=False` + no session | Falls back to component / setting default |
| Data-mode JSON | `data.encoded` decodes with `FusionDecoder` |
| Data-mode JSON | `data.meta.site.navigation` lists Site applications |
| Dashboard data mode | Stats + recent enrollments serialized |
| Language switched (`?lang=ar`) | `meta.language` reflects active locale |

---

> **See also:**
> - [ASTRO_MIGRATION_PLAN.md](./ASTRO_MIGRATION_PLAN.md)
> - [django-fusion AGENTS.md](../../libs/django-fusion/AGENTS.md)
> - [FUSION_LMS_CMS_DESIGN.md](../../docs/FUSION_LMS_CMS_DESIGN.md)
