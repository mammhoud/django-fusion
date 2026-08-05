# Analysis: Replacing FusionProxy with `{% comp %}` + HTMX for Static Content

> Date: 2026-07-31
> Status: Analysis (not a plan)
> Tags: `analysis`, `htmx`, `fusion-proxy`, `component-system`

---

## 1. Current Architecture

### 1.1 The Rendering Pipeline

```
Browser → Next.js SSR → FusionProxy (React) → fetch(fragment_url)
                                                 ↓
                                   Django API View → render template → HTML string
                                                 ↓
                                   dangerouslySetInnerHTML ← injected into React DOM
```

### 1.2 The Two FusionProxy Implementations

| Aspect | LMS FusionProxy | CMS FusionProxy |
|--------|----------------|-----------------|
| **Fragment source** | Wagtail page API (`/api/pages/<slug>/`) | Direct fragment URL |
| **Fallback strategy** | fragment → wagtail → data → error | Simple fetch → error |
| **Script re-eval** | Not needed | Optional via `enableScripts` prop |
| **Loading state** | Skeleton with `data-testid="fusion-loading"` | `LoadingSkeleton` component |
| **Bundle cost** | ~8KB+ React component tree | Smaller React component |

Both components:
1. Fetch an HTML string from a backend endpoint
2. Inject it into the DOM via `dangerouslySetInnerHTML`
3. This bypasses React's virtual DOM for the content area

### 1.3 The Backend Endpoints

The LMS backend provides these endpoints:
- `GET /api/pages/<slug>/data/` → JSON (page metadata for Wagtail rendering)
- `GET /api/pages/<slug>/fragment/` → Fragment pointer (JSON with fragment_url)
- `GET /api/pages/<slug>/fragment?render=1` → HTML fragment (server-rendered)

When `fusion_render_first=True`, the Django server renders the full HTML, and FusionProxy injects it directly.

---

## 2. The django-fusion Component System

### 2.1 The `{% comp %}` Tag

The `{% comp %}` tag is the canonical rendering mechanism:

```django
{% comp "pages.home.hero" heading="Welcome" /%}

{% comp "components.card" %}
  Default slot content
{% endcomp %}
```

It resolves dotted names to template paths:
- `"pages.home.hero"` → `"pages/home/hero.html"`
- `"components.card"` → `"components/card.html"`

### 2.2 FragmentComponent

`FragmentComponent` extends `RoutableComponent` with native HTMX support:

```python
class PostListFragment(FragmentComponent):
    route_name = "post-list-fragment"
    route_path = "posts/list-fragment/"
    fragment_name = "blog.fragments.post_list"
    htmx_only = True
    paginate_by = 10
```

Key features:
- `htmx_only=True` → rejects non-HTMX requests with 400
- `oob_fragments` → out-of-band swaps via `hx-swap-oob`
- Auto-pagination for list fragments
- `FragmentRequestRenderer` handles the rendering

### 2.3 FragmentRequestRenderer

The `FragmentRequestRenderer` converts dotted fragment names to template paths and renders them:

```python
renderer = FragmentRequestRenderer(request, context=base_context)
response = renderer.render("pages.home.hero")
# → renders "pages/home/hero.html" with context
# → sets HX-Reswap header for HTMX requests
```

It also supports SSE streaming via `SSHTMXFragmentStreamer`.

### 2.4 FusionLayout

The `{% fusion_layout %}` tag is defined in `django_fusion/comp/templatetags/fusion_layout.py` and wraps page content with the appropriate layout template (default, full_width, sidebar, blank).

---

## 3. The HTMX Replacement Strategy

### 3.1 The Core Idea

Instead of:

```
Next.js SSR → React FusionProxy → fetch → dangerouslySetInnerHTML
```

Do:

```
Django SSR → HTML with hx-get attributes → HTMX swaps fragments directly
```

This eliminates the React middleman for content rendering. The backend already has all the infrastructure:

- `django_htmx` middleware **already installed** (`configs/base/middlewares.py`)
- `FragmentComponent` and `FragmentRequestRenderer` **ready to use**
- HTMX templates **already working** (auth, cart, forms, modals, pagination)

### 3.2 The Hybrid Approach (Recommended)

A **hybrid approach** works best — not a complete replacement:

| Content Type | Renderer | Why |
|-------------|----------|-----|
| **Static pages** (home, about, contact) | HTMX via `{% comp %}` | No interactivity needed, faster initial load, better SEO |
| **Interactive pages** (dashboard, courses) | React FusionProxy | Needs interactivity, state management |
| **Auth flows** | HTMX (already working) | Already implemented |
| **List views** (courses, events) | HTMX with pagination | FragmentComponent handles this natively |

### 3.3 How It Would Work

#### Step 1: Django template emits HTMX-compatible HTML with `{% comp %}` tags

```django
{# backend/templates/pages/home.html #}
{% extends "base.html" %}

{% block body %}
  {# Hero section: loaded directly (no HTMX needed) #}
  {% comp "pages.home.hero" heading=page.hero_heading /%}

  {# Featured courses: loaded via HTMX on page load #}
  <div id="featured-courses"
       hx-get="{% url 'fragments:featured-courses' %}"
       hx-trigger="load"
       hx-swap="innerHTML">
    <div class="skeleton">Loading courses...</div>
  </div>

  {# Contact form: uses HTMX for submission (already exists) #}
  {% comp "pages.home.contact" /%}
{% endblock %}
```

#### Step 2: FragmentComponent on the backend

```python
class FeaturedCoursesFragment(FragmentComponent):
    route_name = "featured-courses"
    route_path = "fragments/featured-courses/"
    fragment_name = "fragments.featured_courses"
    htmx_only = True

    def get_queryset(self):
        return Course.objects.filter(is_featured=True)

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["courses"] = self.get_queryset()[:6]
        return context
```

#### Step 3: Fragment template

```django
{# templates/fragments/featured_courses.html #}
{% comp "components/course_grid" courses=courses /%}
```

#### Step 4: Next.js route uses HTMX skeleton (minimal React)

```tsx
// app/[slug]/page.tsx
export default function Page({ params }: { params: { slug: string } }) {
  return (
    <main>
      {/* This div's content is loaded directly from Django via HTMX */}
      <div data-htmx-area="page-content"
           hx-get={`/api/pages/${params.slug}/render/`}
           hx-trigger="load"
           hx-swap="innerHTML"
           hx-target="this">
        <LoadingSkeleton />
      </div>
    </main>
  );
}
```

---

## 4. Comparative Analysis

### 4.1 Bundle Size Impact

| Approach | JS Bundle | Notes |
|----------|-----------|-------|
| Current (React FusionProxy) | ~8KB component + ~85KB React runtime | React loaded regardless |
| Pure HTMX | ~14KB (htmx.min.js) | No React needed for static pages |
| Hybrid (React + HTMX) | ~14KB (HTMX) + React when needed | Best of both worlds |

### 4.2 SEO Impact

| Factor | Current (React CSR) | HTMX (SSR) |
|--------|--------------------|------------|
| Initial HTML | Skeleton/loading | Full content |
| Google Indexing | Needs JS rendering | Content in source HTML |
| Time-to-content | Waterfall: React → fetch → render | Direct from first response |

### 4.3 Developer Experience

| Factor | Current | HTMX |
|--------|---------|------|
| Template changes | Update React + Django | Update Django only |
| Debugging | React DevTools + network | Browser DevTools + HTMX events |
| State management | React context/state | `hx-vals`, form serialization |
| Test complexity | Playwright (browser) + pytest | Django test client + Playwright |

### 4.4 Backend Changes Required

| What | Effort | Risk |
|------|--------|------|
| Add `FragmentComponent` views per page | Medium (5-10 view classes) | Low |
| Create fragment templates | Medium (migrate from Wagtail) | Low |
| Add HTMX endpoint routing | Small (1 URL config) | Low |
| Remove FusionProxy from static pages | Medium (conditional imports) | Medium |
| Keep React for interactive pages | None (already works) | None |

### 4.5 Migration Path

```
Phase 1: Add HTMX alongside FusionProxy (no removal)
  - Register FragmentComponent endpoints
  - Create fragment templates for static pages
  - Let HTMX handle lazy page loads via hx-trigger="load"

Phase 2: Remove React FusionProxy for static pages
  - Update Next.js routes to skip FusionProxy for known static slugs
  - Let HTMX load content directly from Django
  - Keep FusionProxy for dynamic pages (dashboard, courses)

Phase 3: Optimize
  - Add hx-boost for full-page navigation without Next.js
  - Add progressive enhancement with Alpine.js
  - Remove unused React bundles
```

---

## 5. Technical Constraints & Concerns

### 5.1 HTMX Must Be Served from the Same Origin

HTMX works via standard HTTP requests to the same origin. The current architecture has:
- Next.js on port 3000 (or 3001)
- Django on port 5074/5075

**Solution:** The nginx/Traefik proxy already routes both. HTMX requests can go directly to `/api/pages/<slug>/fragment/` on the same origin.

### 5.2 CSRF Token Handling

HTMX POST requests need CSRF tokens. The Django backend already handles this:
- `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` in forms
- Meta tag extraction via `document.querySelector('meta[name="csrf-token"]')`

The existing auth templates already use this pattern.

### 5.3 Script Re-evaluation

HTMX natively handles inline `<script>` tags when swapping content — no manual `enableScripts` logic needed. This eliminates the most fragile part of FusionProxy.

### 5.4 Wagtail Integration

Wagtail pages currently use `fusion_before_serve` hooks and `{% fusion_layout %}` template tags. These are all Django template mechanisms — they work perfectly with HTMX without changes. The Wagtail admin is already a separate URL space.

---

## 6. Existing HTMX Usage Already in Place

The codebase already uses HTMX extensively:

| Area | Files | Pattern |
|------|-------|---------|
| **Auth** | 20+ templates | Form submission, fragment swaps |
| **Cart** | `cart/items.html` | Quantity controls, remove items |
| **Forms** | `components/form/form.html` | HTMX-aware form template |
| **Modals** | `components/modal/modal.html` | HTMX trigger + modal skeleton |
| **Pagination** | `components/pagination/` | Infinite scroll, load more |
| **Contact form** | `home/sections/contact.html` | HTMX form submission |

These all work because:
1. `django_htmx` middleware is in `MIDDLEWARE` ✅
2. `django_fusion` FragmentComponent system is available ✅
3. The `{% comp %}` tag resolves to the same template paths ✅

---

## 7. Conclusion

### What HTMX + `{% comp %}` Would Replace

- **FusionProxy for static pages** (home, about, contact, team, services) — fully replaceable
- **Loading skeletons** — handled by HTMX's `hx-indicator` or initial HTML
- **dangerouslySetInnerHTML** — eliminated for static content
- **Manual script re-evaluation** — HTMX does this natively

### What Would Stay as React

- **Dashboard** (needs real-time state, Redux, RTK Query)
- **Course detail** (needs interactivity, enrollment flow)
- **Admin panel** (complex JS widgets)
- **Auth** (already using HTMX — just needs to stay consistent)

### The Hybrid Architecture

```
                    ┌──────────────────────────────────────┐
                    │     Browser                          │
                    │                                      │
                    │  ┌─────────────────────────────────┐  │
                    │  │  Static Pages (HTMX + {% comp %})│  │
                    │  │  - Home, About, Contact         │  │
                    │  │  - Courses list, Events          │  │
                    │  │  - Fragment-based components     │  │
                    │  └─────────────────────────────────┘  │
                    │                                      │
                    │  ┌─────────────────────────────────┐  │
                    │  │  Interactive (React + FusionProxy)│ │
                    │  │  - Dashboard, Course detail      │  │
                    │  │  - Admin, RTK Query pages         │  │
                    │  └─────────────────────────────────┘  │
                    │                                      │
                    │  ┌─────────────────────────────────┐  │
                    │  │  Auth (HTMX - already works)    │  │
                    │  └─────────────────────────────────┘  │
                    └──────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Django (SSR)           Next.js (SSR/CSR)
              - {% comp %} tags      - React components
              - FragmentComponent    - FusionProxy (dynamic)
              - Wagtail pages        - RTK Query
              - HTMX handlers        - Interactive widgets
```

This is **already partially implemented** — the FragmentComponent system is production-ready. The missing piece is the frontend-side HTMX integration in the Next.js layout to replace FusionProxy for static content.
