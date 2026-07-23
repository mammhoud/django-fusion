# django-fusion Components — Agent Instructions

Path: `applications/libs/django-fusion/src/django_fusion/comp/templates/components/`

## Purpose

Reusable, framework-agnostic Django template components shipped with django-fusion.
All components here are pre-registered at app startup (see `CoreExtAppConfig.ready()`
in `django_fusion/comp/apps.py`) so callers can use `{% comp "components/<path>" / %}`
without manual setup.

Components here are **shared across all Structa Cloud sites** (CTC Research, LMS Demo,
VResume, CRM) and contain no site-specific copy or business logic. Site-level or
Wagtail-block variants live one level down in the consumer projects.

## Component Inventory

### Forms & Inputs

| Component | Template | Usage |
|-----------|----------|-------|
| Unified form | `form/form.html` | Standard form w/ HTMX, multipart, cancel button, per-field success hint. Canonical renderer; block-extendable. |
| Form block | `form/form_block.html` | Wagtail StreamField form block (HTMX + multipart, privacy consent, reCAPTCHA, success/error templates). Block-extendable. |
| Form field | `form/form_field.html` | Single-field renderer (textarea/select/checkbox/radio/file/text). Block-aware with per-call BEM class overrides. |
| Simple form | `form/form_simple.html` | Non-HTMX form. Method/action control, `{% block actions %}` override. |
| Submit button | `submit_button.html` | Form-submit button with inline HTMX indicator spinner. Place INSIDE the user's `<form>`. |
| Generic button | `button.html` | `<button>`/`<a>` switch, BEM variants: `border-gradient`, `primary`, `outline-primary`, etc. |

### Modals

| Component | Template | Usage |
|-----------|----------|-------|
| Modal + HTMX trigger | `modal.html` | Combined trigger + skeleton w/ size, centered, scrollable options. |
| Modal trigger only | `modal_trigger.html` | Standalone button that loads content into a separate modal skeleton. |
| Static modal | `modal_static.html` | Block-extendable modal skeleton (no trigger). |

### Notifications

| Component | Template | Usage |
|-----------|----------|-------|
| Notification system | `notification.html` | Toasts/alerts/popups/Django messages/SSE indicator. Includes JS API for `showToast`/`showAlert`/`showErrorAlert`/`showPopup`. |
| Small notification | `notification_small.html` | Inline status pill for form/list/section messages. |

### Pagination

| Component | Template | Usage |
|-----------|----------|-------|
| Unified pagination | `pagination.html` | Prev/next/numbered + ellipsis + HTMX + Unpoly. |
| Numbers-only pagination | `pagination/numbers.html` | Lightweight numbered pages (no HTMX). |
| Load More | `pagination/load_more.html` | "Load More" button that appends next page via HTMX. |
| Infinite scroll | `pagination/infinite.html` | Intersection-observer sentinel via HTMX. |

### Tables & Search

| Component | Template | Usage |
|-----------|----------|-------|
| Table | `table.html` | django-tables2 + explicit headers/rows, HTMX sort links, empty-state. |
| Search | `search.html` | HTMX search form with hidden filter preservation. |
| Breadcrumbs | `breadcrumbs.html` | Schema.org BreadcrumbList + Unpoly/HTMX. |

### Chat & Cookies

| Component | Template | Usage |
|-----------|----------|-------|
| Chat bubble | `chat/bubble.html` | Floating widget + slide-up panel (ceptor/nawaai integration via ceptor-ai). |
| Cookie consent | `cookies/cookie-consent.html` | Cookie preferences UI (essential/analytics/marketing/preferences). Cloned into a modal by cookie-consent.js. |
| Cookie policy | `cookies/cookie-policy.html` | Default cookie policy modal content. |
| Privacy policy | `cookies/privacy-policy.html` | Default privacy policy modal content. |

### Navigation

| Component | Template | Usage |
|-----------|----------|-------|
| App menu | `menu/app_menu.html` | Application-level navigation menu. |
| Site menu | `menu/site_menu.html` | Site-level navigation menu. |
| Nav link | `navigation/nav_link.html` | Single navigation link w/ Unpoly/HTMX. |
| Nav panel | `navigation/nav_panel.html` | Navigation panel wrapper. |

## Conventions

- All components are auto-registered via `register_include_paths([...])` in
  `django_fusion/comp/apps.py.CoreExtAppConfig.ready()`.
- BEM class names (e.g. `notification-system__toast`); no IDs for styling.
- Use `fragment_name="..."` for HTMX fragment identifiers when defining new
  components; never use legacy `fragment`, `fragment_slug`, or `fragment_key`.
- Pass only required context via `{% comp "path" key=val /%}` — never assume
  global context.
- All templates `{% load i18n %}` at the top (and additional libs as needed).
- Static templates follow Django template syntax only — no framework-specific
  DSL. JS shipped inside templates is wrapped in inline `<script>` blocks.

## Migration Status

Templates were migrated from `applications/assets/templates/` into this
package so they ship once as canonical implementations. Legacy paths in
`applications/assets/templates/components/`, `applications/assets/templates/plugins/`,
and `applications/assets/templates/generic/` were retired — callers keep
working seamlessly because Django's template loader resolves the path
through this package's app-template directory.

### Shim retirement

All package-internal and asset-side shims that previously delegated to a
canonical component have been deleted. **There is no `components/form.html`
shim** — callers must use `components/form/form.html` directly. The
backward-compat shims `components/pagination/htmx_pagination.html` and
`plugins/tables/table.html` have also been removed. If a consumer still
references one of these paths it will hit `TemplateDoesNotExist`; the fix
is to update the call site to the canonical path (see the inventory above).

Wagtail-block-component duplicates (e.g. `blocks/partials/form_field.html`, `blocks/partials/enhanced_table.html`, `blocks/content/button_block.html`) remain in the assets tree because their core context (`block`, `page`, Wagtail stream-field tokens) is site-specific. The canonical Wagtail form block (`form/form_block.html`) lives in django-fusion; site-level block subclasses may extend it via `{% extends "components/form/form_block.html" %}`.
