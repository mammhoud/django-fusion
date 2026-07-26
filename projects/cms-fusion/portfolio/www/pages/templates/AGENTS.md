# App Template Guide — Pages App (Portfolio)

**Path:** `projects/portfolio/www/pages/templates/` — App-level page templates

## Scope
App-specific templates for the Pages app in the Portfolio/VResume site. Home, About, Resume, Blog, Portfolio, and Events page templates. Also serves as an override layer for site-specific branding.

## Resolution Context
```
1. Site templates (projects/portfolio/templates/)           ← highest priority
2. App page templates (this directory)                       ← you are here
3. Plugin templates (projects/portfolio/plugins/**/templates/)
4. Shared templates (projects/assets/templates/)             ← fallback
```

## Quick Reference

### Page Models & Their Templates
| Model | App | Expected Template | Route |
|-------|-----|------------------|-------|
| HomePage | `pages.home` | `home/main.html` | `/` |
| AboutPage | `pages.about` | `about/main.html` | `/about/` |
| ResumePage | `pages.cv` | `cv/main.html` | `/resume/` |
| ContactPage | `pages.connect` | `connect/main.html` | `/contact/` |
| PortfolioPage | `pages.portfolio` | `portfolio/main.html` | `/portfolio/` |
| BlogPage | `pages.blog` | `blog/main.html` | `/blog/` |
| EventPage | `pages.events` | `events/main.html` | `/events/` |

### Available Components
| Component | Tag |
|-----------|-----|
| Form | `{% comp "form/form" /%}` |
| Modal | `{% comp "modal/modal" /%}` |
| Pagination | `{% comp "pagination/numbers" /%}` |
| Notification | `{% comp "notification" /%}` |
| Table | `{% comp "table" /%}` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` |
| Search | `{% comp "search/search" /%}` |

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables and block tags
- Portfolio uses tab-based dispatch — fragment templates render into tab content

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Each page app has `main.html` (full page) and `fragment.html` (HTMX fragment)
