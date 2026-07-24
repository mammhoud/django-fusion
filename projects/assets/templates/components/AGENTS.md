# Components Library — AI Agent Instructions

Path: `projects/assets/templates/components/`

## Purpose

Shared, reusable Django/Wagtail template components used across all Structa Cloud sites (LMS, Portfolio, Cypercloud, CTC Research). Components are loaded via `{% comp "path" /%}` (django-fusion) or `{% include "path" %}`.

---

## Component Inventory

### Chat
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Chat Bubble | `chat/bubble.html` | `message`, `role`, `timestamp` | AI chat message bubble |

### Cookies & Privacy
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Cookie Consent | `cookies/cookie-consent.html` | `cookie_settings_url` | GDPR cookie consent banner |
| Cookie Policy | `cookies/cookie-policy.html` | — | Full cookie policy page content |
| Privacy Policy | `cookies/privacy-policy.html` | — | Full privacy policy page content |
| Privacy Consent | `cookies/privacy-consent.html` | `form` | Privacy consent checkbox |

### Forms
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Form | `form/form.html` | `form` (Django Form) | Standard form rendering |
| Form Block | `form/form_block.html` | `form`, `block_id` | Form as content block |
| Form Field | `form/form_field.html` | `field` | Single form field rendering |
| Form Simple | `form/form_simple.html` | `form` | Minimal inline form |

### Modals
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Modal | `modal/modal.html` | `modal_id`, `title`, `content` | Base modal dialog |
| Modal Static | `modal/modal_static.html` | `modal_id`, `title` | Static modal (CSS show/hide) |
| Modal Trigger | `modal/modal_trigger.html` | `target_modal_id` | Button/link that triggers modal |

### Pagination
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Infinite Scroll | `pagination/infinite.html` | `next_page_url` | HTMX infinite scroll trigger |
| Load More | `pagination/load_more.html` | `page_obj` | "Load More" button pagination |
| Numbers | `pagination/numbers.html` | `page_obj` | Numbered pagination links |

### Tables & Search
| Component | Template | Context | Usage |
|-----------|----------|---------|-------|
| Table | `plugins/tables/table.html` | `headers`, `rows` | Data table with headers |
| Search | `search/search.html` | `form` | HTMX search form |

---

## django-fusion Components

The django-fusion library ships additional built-in components (auto-registered). These are the **canonical** implementations and should be preferred when django-fusion is installed.

> ⚠️ **Note**: These components live in `libs/django-fusion/src/django_fusion/comp/templates/components/` — NOT in this directory. Do not duplicate or override them here. If you need to modify a component, modify it in django-fusion's source.

| Component | Path | Purpose |
|-----------|------|---------|
| Unified Form | `components/form/form.html` | HTMX-aware form with multipart, cancel, success hint |
| Form Block | `components/form/form_block.html` | Wagtail StreamField form block |
| Form Field | `components/form/form_field.html` | Per-field renderer with BEM classes |
| Simple Form | `components/form/form_simple.html` | Non-HTMX form |
| Submit Button | `components/submit_button.html` | Form-submit with HTMX indicator |
| Button | `components/button.html` | `<button>`/`<a>` switch, BEM variants |
| Modal | `components/modal.html` | Combined trigger + skeleton |
| Modal Static | `components/modal_static.html` | Block-extendable modal skeleton |
| Notification | `components/notification.html` | Toasts/alerts/popups with JS API |
| Pagination | `components/pagination.html` | Unified pagination with HTMX |
| Table | `components/table.html` | django-tables2 + HTMX sort links |
| Search | `components/search.html` | HTMX search with filter preservation |
| Breadcrumbs | `components/breadcrumbs.html` | Schema.org BreadcrumbList |
| Chat Bubble | `components/chat/bubble.html` | Floating widget + slide-up panel |
| Cookie Consent | `components/cookies/cookie-consent.html` | Cookie preferences UI |
| App Menu | `components/menu/app_menu.html` | Application-level navigation |
| Site Menu | `components/menu/site_menu.html` | Site-level navigation |
| Nav Link | `components/navigation/nav_link.html` | Single nav link |
| Nav Panel | `components/navigation/nav_panel.html` | Nav panel wrapper |

---

## Conventions

- Use `fragment_name` for HTMX fragment identifiers and context keys
- BEM classes: `component`, `component__element`, `component--modifier`
- No IDs for styling
- Pass only required context via `{% include "components/..." with key=value only %}`
- Prefer `{% comp "path" /%}` for component rendering (auto-registered by django-fusion)
- All templates `{% load i18n %}` at minimum

---

## Migration Status

Templates have been migrated from legacy locations into canonical paths. Older shim paths (`components/pagination/htmx_pagination.html`, `plugins/tables/table.html`) have been removed — update call sites to canonical paths if encountering `TemplateDoesNotExist`.
