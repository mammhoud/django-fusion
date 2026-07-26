# Site Template Overrides — Portfolio/VResume

**Path:** `projects/portfolio/templates/` — Site-specific template overrides

## Lookup Strategy
Site templates here are resolved before the shared template layer. Keep files here only for intentional site-specific overrides, branded shells, or shadowed behavior.

## Resolution Context
```
1. Site templates (this directory)                                      ← highest priority (you are here)
2. App page templates (projects/portfolio/www/pages/**/templates/)
3. Plugin templates (projects/portfolio/plugins/**/templates/)
4. Shared templates (projects/assets/templates/)                        ← fallback
```

## Additional Template Directories
- `projects/portfolio/www/pages/templates/` — page-level templates
- `projects/portfolio/www/pages/connect/templates/` — connect/contact templates
- `projects/portfolio/plugins/accounts/templates/` — account/auth plugins

## Override Rules
- Prefer deleting exact duplicates and letting Django load shared templates
- Keep thin overrides for branded variations; move reusable markup into shared includes
- Preserve existing template names, include names, block names, and context variables
- Use `fragment_name` for fragment identifiers and context keys
- When adding or changing an override, compare same relative path in shared templates first

## Quick Reference

### VResume-Specific Page Models
| Model | Template | Route |
|-------|----------|-------|
| HomePage | `home/home_page.html` | `/` |
| AboutPage | `about/about_page.html` | `/about/` |
| ResumePage | `cv/resume_page.html` | `/resume/` |
| ContactPage | `connect/contact_page.html` | `/contact/` |
| PortfolioPage | `portfolio/portfolio_page.html` | `/portfolio/` |
| BlogPage | `blog/blog_page.html` | `/blog/` |
| EventPage | `events/event_page.html` | `/events/` |

### Tab-Based Navigation
Portfolio uses a unique tab-based layout. Each tab dispatches to its fragment template.
| Tab | Fragment Template |
|-----|-------------------|
| Home | `home/pages/fragment.html` |
| About | `about/pages/fragment.html` |
| Resume | `cv/fragment.html` |
| Portfolio | `portfolio/fragment.html` |
| Blog | `blog/fragment.html` |
| Contact | `connect/fragment.html` |

### Available Components
| Component | Tag |
|-----------|-----|
| Form | `{% comp "form/form" /%}` |
| Modal | `{% comp "modal/modal" /%}` |
| Pagination | `{% comp "pagination/numbers" /%}` |
| Notification | `{% comp "notification" /%}` |
| Table | `{% comp "table" /%}` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` |

## Conventions
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Prefer `{% comp "path" /%}` over `{% include %}` when possible
- Use `fragment_name` for HTMX fragment responses

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Portfolio uses tab-based navigation — extend tab block, don't replace skeleton
