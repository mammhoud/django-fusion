# VResume

> **Site:** `applications/VResume/` · **Domain:** https://vresume.structa.cloud
> **Variant:** `layout/landing/skeleton.html`
> **Routing style:** RoutableComponent + FragmentComponent + Wagtail Pages
> **AGENTS:** [`applications/VResume/AGENTS.md`](../../../applications/VResume/AGENTS.md)
> **Prompts:** [`applications/VResume/PROMPTS.md`](../../../applications/VResume/PROMPTS.md)

---

## Architecture Overview

VResume is the **CMS-leaning portfolio/blog surface** — the broadest exercise of django-fusion's
`RoutableComponent`, `FragmentComponent`, and `Application` patterns. Unlike the LMS sites
(ctc-research + lms-demo), VResume uses tab-based navigation driven by `{% block vresume_content %}`,
with each tab dispatching to its fragment template via HTMX.

### Site / Application Tree

```
VResumeSite (Site)
├── BlogApp (Application)
│   ├── BlogListComponent (FragmentComponent)    — /blog/
│   └── BlogDetailComponent (RoutableComponent)  — /blog/<slug>/
├── PortfolioApp (Application)
│   ├── ProjectList (RoutableComponent)           — /portfolio/
│   └── ProjectDetail (RoutableComponent)         — /portfolio/<int:id>/
├── EventsApp (Application)
│   ├── EventList (RoutableComponent)             — /events/
│   └── EventGridFragment (FragmentComponent)     — /events/grid/
├── ConnectApp (Application)                      — /contact/
├── AboutApp (Application)                        — /about/
├── CVApp (Application)                           — /resume/
└── Account (Application)                         — /accounts/ (allauth)
```

### Template Resolution

1. `VResume/templates/` — site overrides (highest)
2. `VResume/www/pages/<app>/templates/` — app-level page templates
3. `VResume/plugins/<name>/templates/` — plugin templates
4. `assets/templates/` — shared templates (lowest)

### Page Models

| Model | App | Template | Route |
|-------|-----|----------|-------|
| HomePage | `VResume.www.pages.home` | `home/home_page.html` | `/` |
| AboutPage | `VResume.www.pages.about` | `about/about_page.html` | `/about/` |
| ResumePage | `VResume.www.pages.cv` | `cv/resume_page.html` | `/resume/` |
| ContactPage | `VResume.www.pages.connect` | `connect/contact_page.html` | `/contact/` |
| PortfolioPage | `VResume.www.pages.portfolio` | `portfolio/portfolio_page.html` | `/portfolio/` |
| BlogPage | `VResume.www.pages.blog` | `blog/blog_page.html` | `/blog/` |
| EventPage | `VResume.www.pages.events` | `events/event_page.html` | `/events/` |

### Tab-Based Navigation

VResume uses a unique tab-based layout in `base.html`:
- **Tabs:** home, about, resume, portfolio, blog, contact
- Content rendered via `{% block vresume_content %}`
- Each tab dispatches to its fragment template via HTMX
- Legacy slug redirects: `/home-page/` → `/`, `/about-page/` → `/about/`, `/team-page/` → `/team/`, `/contact-page/` → `/contact/`

### Layout Variants

| Variant | Use Case |
|---------|----------|
| `layout/landing/` | All public-facing pages (primary variant) |
| `layout/auth/` | Login, signup |

### Auth & Accounts

- **Adapter:** `plugins.accounts.adapters.RegistrationAdapter`
- **Social auth:** `AuthHTMXSocialAccountAdapter` configured in `plugins/accounts/adapters.py`
- **MFA:** TOTP UI not yet present (planned — see upcoming specs)
- **Account URLs:** exposed at `/accounts/` (allauth)

### Fragment Naming

All HTMX fragments use dot-notation: `vresume.fragments.<app>.<name>`
- `vresume.fragments.blog.post_detail` — blog post detail
- `vresume.fragments.blog.post_preview` — blog post preview
- `vresume.fragments.events.grid` — events grid

---

## Site-Specific Patterns

1. **No Wagtail StreamField body blocks**: Pages are plain Django models using `FragmentComponent` for HTMX navigation — not Wagtail StreamField-based layouts.
2. **Scope**: home, about, resume/CV, portfolio, blog, contact, events — no LMS or products plugins.
3. **`VResume/templates/` is intentionally sparse**: Prefer shared templates in `assets/templates/` for cross-site components.
4. **Tab-based layout**: `VResume/www/pages/templates/base.html` renders the tab bar; each tab's content fills `{% block vresume_content %}`.
5. **For new page models**: Extend `VResume.www.pages.BasePage` (or the site's existing base) before `Page`.

---

## Commands

```bash
# Django checks
make -C applications check WEBSITE=vresume

# Run tests
make -C applications test WEBSITE=vresume

# Migrate
make -C applications makemigrations WEBSITE=vresume
make -C applications migrate WEBSITE=vresume

# Frontend assets
make -C applications/VResume build

# Lint
make -C applications lint

# Collect static
make -C applications collectstatic WEBSITE=vresume
```

---

## See Also

- [`applications/VResume/AGENTS.md`](../../../applications/VResume/AGENTS.md) — template tree, page models table, step-by-step task guides
- [`applications/VResume/PROMPTS.md`](../../../applications/VResume/PROMPTS.md) — AI prompt catalog for VResume
- [`../../../applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`](../../../applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md) — RoutableComponent, FragmentComponent, lifecycle
- [`../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md`](../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md) — `{% comp %}` props/slots/vars reference
- [`../../../applications/libs/django-fusion/docs/ROUTING_SYSTEM.md`](../../../applications/libs/django-fusion/docs/ROUTING_SYSTEM.md) — URL routing and navigation
- [`../../architecture/routable_site.md`](../../reference/architecture/routable_site.md) — Site registration patterns
