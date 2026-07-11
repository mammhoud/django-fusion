# Components Library — Agent Instructions

Path: `core/assets/templates/components/`

## Purpose

Shared, reusable Django/Wagtail template components used across all Structa Cloud sites
(CTC Research, LMS Demo, VResume). Components are loaded via `{% include %}` or the
custom `{% comp %}` tag (requires `django_fusion.comp`).

## Component Inventory

### Chat
| Component | Template | Usage |
|-----------|----------|-------|
| Chat Bubble | `chat/bubble.html` | AI chat message bubble; expects `message`, `role`, `timestamp` context |

### Cookies & Privacy
| Component | Template | Usage |
|-----------|----------|-------|
| Cookie Consent | `cookies/cookie-consent.html` | GDPR cookie consent banner; expects `cookie_settings_url` |
| Cookie Policy | `cookies/cookie-policy.html` | Full cookie policy page content |
| Privacy Policy | `cookies/privacy-policy.html` | Full privacy policy page content |

### Forms
| Component | Template | Usage |
|-----------|----------|-------|
| Form | `form/form.html` | Standard form rendering; expects `form` context (Django Form) |
| Form Block | `form/form_block.html` | Form rendered as a content block; expects `form` and `block_id` |
| Form Field | `form/form_field.html` | Single form field rendering; expects `field` context |
| Form Simple | `form/form_simple.html` | Minimal form with inline layout |

### Modals
| Component | Template | Usage |
|-----------|----------|-------|
| Modal | `modal/modal.html` | Base modal dialog; expects `modal_id`, `title`, `content` |
| Modal Static | `modal/modal_static.html` | Static modal (always rendered, shown/hidden via CSS) |
| Modal Trigger | `modal/modal_trigger.html` | Button/link that triggers a modal; expects `target_modal_id` |

### Pagination
| Component | Template | Usage |
|-----------|----------|-------|
| Infinite Scroll | `pagination/infinite.html` | HTMX infinite scroll trigger; expects `next_page_url` |
| Load More | `pagination/load_more.html` | "Load More" button pagination; expects `page_obj` |
| Numbers | `pagination/numbers.html` | Numbered pagination links; expects `page_obj` |

## Conventions

- Use `fragment_name` for HTMX fragment identifiers and context keys
- BEM classes: `component`, `component__element`, `component--modifier`
- No IDs for styling
- Pass only required context via `{% include "components/..." with key=value only %}`
- Prefer `{% comp "path" /%}` for component rendering (auto-registered by django-fusion)
