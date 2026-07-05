# Django-Osoul Template Architecture Analysis

> **Date:** July 5, 2026  
> **Repository:** Structa Cloud Monorepo  
> **Scope:** `applications/assets/templates/`, site templates, and `django-fusion` library integration

---

## 1. Base Template Architecture

### 1.1 Inheritance Chain

```
base.html (applications/assets/templates/)
  ├── layout/landing/skeleton.html     → [landing pages, home, about]
  │   └── layout/profile/skeleton.html → [profile pages (extends landing)]
  ├── layout/auth/skeleton.html        → [login, register, password reset]
  ├── layout/learning/skeleton.html    → [LMS/course pages]
  ├── layout/apps/meta.html            → [shared <head> metadata]
  └── layout/forms/skeleton.html       → [standalone form pages]
```

### 1.2 `base.html` — The Root Template
**Path:** `applications/assets/templates/base.html`

| Feature | Implementation | Status |
|---------|---------------|--------|
| Webpack bundles | `{% render_bundle 'static' 'css' %}` in `layout_css` block | ✅ Good |
| JS bundles | `{% render_bundle 'main' 'js' %}` + `{% render_bundle 'app' 'js' %}` at body end | ✅ Good |
| CSS framework | Bootstrap 5 via webpack `static` bundle | ✅ Good |
| HTMX | Body-level `hx-headers` for CSRF token | ✅ Good |
| Theme support | `data-sidenav-view`, theme class | ✅ Good |
| RTL support | `dir="{{ LANGUAGE_BIDI|yesno:'rtl,ltr' }}"` | ✅ Good |
| Notifications | Commented out `comp_include` due to RecursionError | ⚠️ **FIXME** |
| Cookie consent | 3x `comp_include` for cookies/privacy | ✅ Good |

**⚠️ Issue — Notifications FIXME:** The notification include is commented out in `base.html` with:
```django
{# FIXME: notification include causes RecursionError in template render chain #}
{# {% comp_include "plugins/notifications/notification.html" %} #}
```
This means the entire unified notification system (toasts, alerts, popups, Django messages) is **not active** in the base template. The notification template is highly sophisticated (see §7 below) but currently inaccessible via this route. Individual layouts like `ui/base_auth.html` handle messages manually with Bootstrap alerts.

### 1.3 `ui/base_page.html` — Generic Page Handler
**Path:** `applications/assets/templates/ui/base_page.html`

```django
{% extends layout_path|default:"landing/skeleton.html" %}
{% load laces %}
{% block content %}
{% if template_name and not fragment_name %}
    {% include template_name %}
{% elif fragment_name %}
    {% comp 'base_fragment' with fragment_name=fragment_name / %}
{% endif %}
{% endblock %}
```
This is the **page routing gateway** — it dynamically chooses between:
- **`template_name` fallback:** Direct `{% include %}` (traditional Django rendering)
- **`fragment_name` path:** Uses `{% comp 'base_fragment' %}` (django-fusion component system)

### 1.4 `ui/base_auth.html` — Authentication Pages
**Path:** `applications/assets/templates/ui/base_auth.html`

Features a **split-layout design** with:
- Welcome section with logo, title, decoration, social proof
- Form section rendering `{% comp fragment_name / %}` or a fallback message

### 1.5 `base_profile.html` — Profile Pages
**Path:** `applications/assets/templates/base_profile.html`

Uses `profile/skeleton.html` layout (extends `landing/skeleton.html`) with:
- Banner with avatar and user info
- Mobile off-canvas navigator
- Sidebar navigation via `comp_include`
- HTMX-targetable panel (`#panel-content`) rendering `{% comp fragment_name / %}`
- 6 profile modals loaded via `comp_include`

---

## 2. Error Pages Analysis

### 2.1 Available Error Templates

| Error | Template | Design Quality | Extends |
|-------|----------|---------------|---------|
| 400 | `plugins/errors/400.html` | Basic (placeholder) | base.html |
| 401 | `plugins/errors/401.html` | Basic (placeholder) | base.html |
| 403 | `plugins/errors/403.html` | **Excellent** — forbidden pattern, access info grid, possible reasons, action buttons | base.html |
| 404 | `plugins/errors/404.html` | **Excellent** — glitch animation, particle bg, floating shapes, search form, quick links, analytics, structured data | base.html |
| 429 | `plugins/errors/429.html` | Basic (placeholder) | base.html |
| 500 | `plugins/errors/500.html` | **Good** — animated shapes, collapsible technical details, error reference ID | base.html |
| 502 | `plugins/errors/502.html` | Basic (placeholder) | base.html |
| 503 | `plugins/errors/503.html` | Basic (placeholder) | base.html |
| 504 | `plugins/errors/504.html` | Basic (placeholder) | base.html |
| nxx | `plugins/errors/nxx.html` | Generic fallback (standalone HTML) | None |

### 2.2 ❌ Missing: ComingSoon Template

**There is NO `comingsoon` or `coming_soon` template anywhere in the project.** A search across all template directories returned zero results.

**Recommendation:** Create `plugins/errors/comingsoon.html` with the same design quality as `404.html` (glitch animation, particles, floating shapes, countdown timer, email subscription form) using the same `base.html` extension pattern. The 404 template serves as the ideal reference design.

---

## 3. Home Page & Layout Systems

### 3.1 Home Page (`home/main.html`)
**Path:** `applications/assets/templates/home/main.html`

Uses **Wagtail StreamField block iteration** with django-fusion's `comp_include`:
- `head` blocks: slider, features, about
- `summary` blocks: about (team/services commented out)
- `listing` courses section
- `CTA` blocks: clients, why_choose, contact (via `{% comp "contact.sections.card" %}`)
- `contact_form` blocks: contact form (via `{% comp "contact.sections.form" %}`)

**Issue:** Several sections are commented out (`team_section`, `services_section`).

### 3.2 Site-Specific `base_page.html` Overrides

#### CTC Research (`ctc-research/templates/base_page.html`)
```django
{% extends "base.html" %}  {# Falls back to assets templates #}
```
Simple fallback to `home/main.html` when no specific template is set. Uses direct `{% include %}` not `comp_include`.

#### LMS Demo (`lms-demo/templates/base_page.html`)
Identical pattern to CTC — extends `base.html`, falls back to `home/main.html`.

#### LMS Demo Auth (`lms-demo/templates/base_auth.html`)
Site-specific copy of `ui/base_auth.html` with one notable addition: a **fallback** when `fragment_name` is not set:
```django
{% else %}
  <div class="auth__component-fallback" role="status">
    {% trans "No authentication form is currently configured." %}
  </div>
{% endif %}
```
The shared `ui/base_auth.html` does **not** have this fallback message.

#### VResume (`VResume/www/pages/templates/base.html`)
**Completely custom** base template (does NOT extend `applications/assets/templates/base.html`):
- Standalone SPA-style layout with fixed sidebar
- Tab-based navigation (About, Resume, Portfolio, Blog, Contact)
- Uses django-fusion components extensively: `comp_include` for sidebar, tab fragments, modals, cookie consent, footer
- Uses `{% comp 'js_i18n' / %}` for JS internationalization
- Has its own metatags handling with `comp_include 'layout/meta.html'`
- Includes cookie consent as comp components (not comp_include)

#### Customizer (`customizer/templates/base.html`)
Minimal standalone base template with:
- Bootstrap via CDN (no webpack)
- HTMX from CDN
- Simple container layout

### 3.3 Layout Skeletons Summary

| Layout | Extension | Use Case | Key Features |
|--------|-----------|----------|-------------|
| `landing/skeleton.html` | base.html | Marketing pages | Header, main shell, footer |
| `auth/skeleton.html` | base.html | Login/Register | Light theme, Passkey support, auth container |
| `learning/skeleton.html` | base.html | LMS courses | Theme 2, LMS shell, course nav |
| `profile/skeleton.html` | landing/skeleton.html | User profile | Profile layout, modal overlay |
| `apps/meta.html` | — | Shared `<head>` | Favicon, SEO meta |
| `forms/skeleton.html` | — | Form pages | HTMX form, reCAPTCHA, templates |

---

## 4. Fragment System Analysis

### 4.1 Core Fragment Template
**Path:** `applications/assets/templates/plugins/base/fragment.html`

```django
{% if fragment_name %}
<div id="{{ fragment_name }}__container">
  {% comp fragment_name / %}
</div>
{% else %}
<div class="fragment__fallback" role="status">
  No fragment component is currently configured.
</div>
{% endif %}
```

This provides a **consistent container** for HTMX OOB swaps and partial re-renders.

### 4.2 Blog Fragments

| Fragment | Path | HTMX | OOB Swaps | Notes |
|----------|------|------|-----------|-------|
| `post_create_form` | `blog/fragments/` | ✅ hx-post | ✅ targets `#post-create-form` | Full form with cancel button |
| `post_list` | `blog/fragments/` | ✅ hx-get for search | ✅ OOB success placeholder | Uses `fragment_pagination` tag |
| `post_count` | `blog/fragments/` | ✅ hx-swap-oob | ✅ standalone OOB | Updates post count badge |
| `post_create_success` | `blog/fragments/` | ✅ hx-swap-oob | ✅ OOB alert | Bootstrap dismissible alert |

### 4.3 Registration Fragments

| Fragment | Path | HTMX | Features |
|----------|------|------|----------|
| `login_form` | `registration/fragments/` | ✅ hx-post to `plugins:login` | Password toggle, remember me |
| `register_form` | `registration/fragments/` | ✅ hx-post | Success state, privacy modal link |
| `password_form` | `registration/fragments/` | ✅ hx-post | Password strength meter, rules checklist |

**Quality:** All registration fragments use BEM-style CSS (`form__validation-message`, `form__input-wrapper--error`) and CSS custom properties (`var(--auth-text-secondary)`). They include proper ARIA attributes and live regions.

### 4.4 Fragment Page Routing
The `index.html` template acts as the main fragment gateway:
```django
{% if htmx_page %}
  {% include htmx_page %}
{% else %}
  {% comp 'base_fragment' / %}
{% endif %}
```

---

## 5. Table Implementations

### 5.1 Simple Table (`plugins/tables/table.html`)
**HTMX-driven sortable table** with:
- Column headers with sort URLs and direction indicators
- Empty state with icon
- Fully parameterized via `headers`, `rows`, `table_class`, `hx_target`

### 5.2 Enhanced Table (`blocks/partials/enhanced_table.html`)
**Wagtail StreamField block** with:
- Search bar (`data-table-search`)
- Export buttons (CSV, Excel, PDF, Print)
- Fixed header support
- Client-side pagination
- Custom caption positioning (top/bottom)
- Uses custom template tags: `get_table_config`, `get_table_classes`, `render_unhandled_fields`

### 5.3 Content Blocks
- `blocks/content/table_block.html` — Auto-generated placeholder
- `blocks/content/typed_table.html` — Auto-generated placeholder

**Issue:** `table_block.html` and `typed_table.html` are **empty auto-generated stubs**. They need actual implementations.

### 5.4 OOP Fragments — Entity Display
The `generic/` directory contains basic CRUD templates for "Customer" as an example:
- `generic/_list.html` — Simple `<ul>` list
- `generic/_detail.html` — Field display with edit/delete actions
- `generic/_form.html` — Standard `form.as_p`
- `generic/_confirm_delete.html` — Confirmation page

**These are basic Django patterns**, not django-fusion components. They should be migrated to use the fragment system for HTMX-enabled row-level operations.

---

## 6. Form Implementations

### 6.1 Three-Tier Form Architecture

| Tier | Template | Use Case | HTMX |
|------|----------|----------|------|
| **L1: Simple** | `components/form/form_simple.html` | Standard POST forms | ❌ |
| **L2: Unified** | `components/form/form.html` | Full-featured Django forms | ✅ Full HTMX |
| **L3: Block** | `layout/forms/skeleton.html` / `form_block.html` | Wagtail StreamField forms | ✅ With reCAPTCHA |

### 6.2 `form.html` — The Flagship Form
**Path:** `applications/assets/templates/components/form/form.html`

Features:
- **Automatic widget detection:** checkbox, radio, file, textarea, select
- **Non-field error summary** with Bootstrap alert
- **Per-field error display** with icons
- **Per-field success hints** (e.g., username availability check)
- **HTMX integration:** `hx-post`, `hx-target`, `hx-swap`, `hx-indicator`
- **Multipart support:** Auto-detection + manual override
- **Cancel button** with configurable behavior
- **Extensive documentation** in template comments

**Form templates found in the wild:**
- `blog/fragments/post_create_form.html` — **Does NOT use** `components/form/form.html`; manually builds form with field-by-field markup. Inconsistent with the shared form system.
- `registration/fragments/login_form.html` — Custom form markup with BEM classes. Not using shared form system.
- `blocks/minimal_contact_form.html` — Custom inline form with its own notification templates.

### 6.3 `form_field.html` — Individual Field Renderer
**Path:** `applications/assets/templates/components/form/form_field.html`

Renders individual fields for Wagtail form blocks with:
- Icons (configurable position/style)
- Label visibility toggle
- Placeholder support
- Help text
- Error containers
- All input types: text, textarea, select, checkbox, radio, file

---

## 7. Notification System

### 7.1 Architecture (`plugins/notifications/notification.html`)
A **comprehensive unified notification system** supporting:

| Notification Type | Trigger Method | Features |
|-------------------|---------------|----------|
| **Django Messages** | `{% if messages %}` → JS processing on DOMContentLoaded | Automatic toast conversion |
| **Toasts** | `showToast(level, message, title, duration)` | Auto-dismiss, positioned top-right |
| **Alerts** | `showAlert(opts)` | Persistent, manual dismiss, badge, details expander |
| **Error Alerts** | `showErrorAlert(message)` | Shorthand for danger-level alerts |
| **Popups** | `showPopup(opts)` | Modal-style, blocks interaction, customizable actions |
| **SSE Live Updates** | `sse-connect` attribute | Real-time notification indicator |
| **HTMX OOB Fragments** | `<template id="toast-success">` etc. | Server-side toast injection via `hx-swap-oob` |

### 7.2 Current Status
- The notification system is **commented out** in `base.html` due to a **RecursionError**
- Individual layouts handle messages with inlined Bootstrap alerts
- The system has 4 concrete HTMX OOB toast templates (success, error, warning, info)
- Test files `a.html`, `b.html`, `c.html`, `d.html` are simple test stubs

### 7.3 Notification Supporting Components
- `plugins/base/error.html` — Inline error alert (HTMX target)
- `plugins/base/validation.html` — Field-level validation feedback
- `plugins/base/confirm.html` — Reusable confirmation modal with HTMX action
- `plugins/base/loader.html` — Three loader variants (spinner, overlay, skeleton)
- `plugins/base/fragment.html` — Fragment container wrapper

---

## 8. Site-Specific Approaches — Comparative Analysis

### 8.1 CTC Research (`ctc-research/`)

| Aspect | Approach | django-fusion Usage |
|--------|----------|-------------------|
| Base template | Extends `assets/templates/base.html` | Minimal — `comp_include` and `comp` in shared templates |
| Page routing | `base_page.html` → `include template_name` | Falls back to `include "home/main.html"` |
| Auth | Via shared `ui/base_auth.html` | `comp fragment_name /` |
| Components | Uses shared component templates | `comp_include` via shared layouts |
| **Gap** | Site-specific `base_page.html` uses basic `{% include %}` not `comp` | Low django-fusion integration |

### 8.2 LMS Demo (`lms-demo/`)

| Aspect | Approach | django-fusion Usage |
|--------|----------|-------------------|
| Base template | Extends `assets/templates/base.html` | Same as CTC |
| Page routing | Identical to CTC | Falls back to `home/main.html` |
| Auth | **Site-specific** `base_auth.html` with fallback message | `comp fragment_name /` |
| Profile | **Site-specific** `base_profile.html` with fallback message | `comp fragment_name /` |
| **Improvement** | Has fallback states CTC doesn't | Higher robustness |

### 8.3 VResume (`VResume/`)

| Aspect | Approach | django-fusion Usage |
|--------|----------|-------------------|
| Base template | **Fully custom** `base.html` (does NOT extend shared) | **Heaviest usage** |
| Layout | SPA shell with fixed sidebar | `comp_include` for sidebar, tab fragments, footer |
| Components | Cookie consent as `comp` (not comp_include) | `comp 'modals.cookie-consent' /` etc. |
| Internationalization | `comp 'js_i18n' /` | Dedicated i18n component |
| Modal system | `comp 'modals.unified-modal' /` | Component-based modal |
| **Pattern** | Most sophisticated django-fusion integration | Reference implementation |

### 8.4 Customizer (`customizer/`)

| Aspect | Approach | django-fusion Usage |
|--------|----------|-------------------|
| Base template | Fully custom minimal base | None |
| CSS/JS | CDN-based (HTMX, Bootstrap) | No webpack |
| **Pattern** | Standalone tool, not part of main template system | N/A |

---

## 9. Pagination Components

Three patterns available:

| Pattern | Template | Mechanism |
|---------|----------|-----------|
| **Numbers** | `components/pagination/numbers.html` | Traditional page links with `?page=` params |
| **Infinite Scroll** | `components/pagination/infinite.html` | HTMX `intersect once` trigger |
| **Load More** | `components/pagination/load_more.html` | Button with HTMX `hx-get` |

The `fragment_pagination` tag from `routable_components` is used in `blog/fragments/post_list.html`.

---

## 10. Component System (django-fusion) Mechanics

### 10.1 Two Rendering Paths

| Tag | Mechanism | Registration | Use Case |
|-----|-----------|-------------|----------|
| `{% comp "name" %}` | Full component pipeline (slots, props, assets) | Auto-discovered or registered | Named components |
| `{% comp_include "path" %}` | Django `render_to_string` + registry tracking | Auto-registered on first use | Migration from `{% include %}` |

### 10.2 `comp_include` Bridge
The `comp_include` tag (`include_bridge.py`):
1. Renders the template via Django's standard `render_to_string`
2. Registers the path in the component registry via `register_include_path`
3. This enables **gradual migration**: `{% include %}` → `{% comp_include %}` → `{% comp %}`

### 10.3 `IncludePathComponent`
When `comp_include` registers a path, an `IncludePathComponent` is created with:
- `name = path` (verbatim, e.g., `"partials/auth_buttons.html"`)
- `template = _LazyIncludeTemplate(path)` (deferred resolution)

---

## 11. Cross-Cutting Concerns

### 11.1 CSS Architecture
- **Bootstrap 5** as the base framework
- **BEM-style** class naming in newer components: `notification-system__toast`, `form__validation-message--error`, `auth__welcome-section--split`
- **CSS custom properties** for theming: `--auth-text-secondary`, `--auth-link-color`
- **Tailwind** referenced in webpack config but not evident in templates

### 11.2 JavaScript Architecture
- **HTMX** for AJAX/interactivity (attribute-driven)
- **Alpine.js** loaded via webpack bundle (referenced in base.html comment)
- **Webpack** builds: `static` (CSS+JS), `main` (shared libs), `app` (site-specific)
- **Bootstrap JS** for modals, dropdowns, toasts, offcanvas

### 11.3 Template Tag Libraries Used

| Library | Usage | Notes |
|---------|-------|-------|
| `laces` | `{% load laces %}` | Custom tag library |
| `unfold` | `{% load unfold %}` | Django Unfold admin theme |
| `webpack_loader` | `{% render_bundle %}` | Webpack integration |
| `wagtailcore_tags` | `{% pageurl %}` etc. | Wagtail CMS |
| `wagtailimages_tags` | `{% image %}` | Wagtail images |
| `wagtailsettings_tags` | Settings access | Wagtail settings |
| `routable_components` | `{% fragment_pagination %}` | django-fusion routing |
| `components_field` | `{% get_table_config %}` etc. | Custom table tags |

---

## 12. TODOs & Recommendations

### 🔴 Critical

| # | Issue | Location | Recommendation |
|---|-------|----------|---------------|
| 1 | **Notifications disabled** | `base.html` L? (commented out) | Fix the RecursionError in the notification include chain. The notification system is highly sophisticated but unusable. |
| 2 | **Missing ComingSoon template** | None exists | Create `plugins/errors/comingsoon.html` matching the 404 design quality with countdown, email subscription, and particle effects. |
| 3 | **Inconsistent page routing** | `ctc-research/base_page.html`, `lms-demo/base_page.html` use `{% include %}` instead of `{% comp %}` or `{% comp_include %}` | Migrate to `comp_include` for tracking and consistency. |

### 🟡 Important

| # | Issue | Location | Recommendation |
|---|-------|----------|---------------|
| 4 | **Form fragmentation** | Blog fragments, registration fragments, contact forms all use different form markup | Standardize on `components/form/form.html` or create a thin adapter. At minimum, document the 3 form patterns and their intended use cases. |
| 5 | **Empty block stubs** | `blocks/content/table_block.html`, `typed_table.html`, `cta_block.html`, `paragraph_block.html` | Implement actual block templates or remove the stubs. |
| 6 | **Fallback inconsistency** | `lms-demo/base_auth.html` has fallback message; shared `ui/base_auth.html` does not | Add fallback to shared template. |
| 7 | **Generic templates outdated** | `generic/_form.html`, `_list.html`, `_detail.html`, `_confirm_delete.html` use basic Django patterns | Migrate to fragment-based HTMX patterns. |
| 8 | **VResume isolation** | VResume `base.html` doesn't extend shared template | Consider extracting shared features (meta, cookie consent, notifications) into reusable `comp` components that both VResume and shared templates can use. |

### 🟢 Nice-to-Have

| # | Issue | Location | Recommendation |
|---|-------|----------|---------------|
| 9 | **Duplicate base_auth** | `lms-demo/templates/base_auth.html` is ~80% duplicate of `ui/base_auth.html` | DRY: extend shared template and only override content block. |
| 10 | **Duplicate base_profile** | `lms-demo/templates/base_profile.html` vs `assets/templates/base_profile.html` | Same DRY concern. |
| 11 | **Commented-out sections** | `home/main.html` — team_section, services_section | Either implement or remove the dead code. |
| 12 | **Error template parity** | 400, 401, 429, 502, 503, 504 are basic placeholders | Apply the same design quality as 403/404/500 to all error codes. |
| 13 | **Table component gap** | No django-fusion `comp`-based table component exists | Create `{% comp 'table' %}` wrapping `plugins/tables/table.html` with slot support. |
| 14 | **Documentation** | No per-site documentation of template customizations | Add a `TEMPLATES.md` in each site directory listing overrides and customizations. |
| 15 | **Fragment catalog** | No index of available fragments | Build an auto-generated fragment registry page (dev mode) listing all `fragment_name` values and their templates. |
| 16 | **Test coverage** | No template-rendering tests for error pages, fragments, or form components | Add template rendering tests for all error codes, form variants, and fragment compositions. |

---

## 13. Summary by Website

### CTC Research (`ctc-research.com`)
- **django-fusion level:** Low
- **Template strategy:** Thin wrapper extending shared templates
- **Page routing:** `include template_name` with `home/main.html` fallback
- **Key gap:** No site-specific component usage, no fragment routing

### LMS Demo (`lms-demo.com`)
- **django-fusion level:** Medium
- **Template strategy:** Site-specific overrides with fallback states
- **Profile pages:** Full sidebar + fragment-based panel with modals
- **Auth pages:** Enhanced with fallback message
- **Key gap:** Still uses `include` not `comp_include` in base_page

### VResume (`vresume.structa.cloud`)
- **django-fusion level:** High
- **Template strategy:** Fully custom SPA layout with component-based architecture
- **Components:** Sidebar, tabs, modals, cookie consent, i18n, footer — all as `comp`
- **Reference implementation** for django-fusion integration

### Customizer
- **django-fusion level:** None
- **Template strategy:** Minimal standalone HTML
- **Use case:** Configuration tool, not content-serving

---

*Analysis compiled from reading 110+ template files across the monorepo and the django-fusion component registry, routing, and template tag source code.*
