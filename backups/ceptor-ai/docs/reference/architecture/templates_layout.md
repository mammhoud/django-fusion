# Templates Layout — Skeleton Chain

> **Related Code**
> * **Domain:** Layouts / Templates
> * **Paths:**
>   * `applications/assets/templates/base.html`
>   * `applications/assets/templates/layout/auth/skeleton.html`
>   * `applications/assets/templates/layout/learning/skeleton.html`
>   * `applications/assets/templates/layout/landing/skeleton.html`
>   * `applications/assets/templates/layout/profile/skeleton.html`
>   * `applications/assets/templates/ui/base_page.html`
>   * `applications/assets/templates/ui/base_auth.html`
> * **Classes / modules:** `django_fusion.comp.templatetags.components`, `webassets.utils`

This document describes the canonical layout chain that every Structa Cloud template inherits from. Each layer adds blocks the next layer can override; the chain is intentionally linear so a developer can predict where any given `{% block %}` resolves.

## The chain

```
base.html                       (root: <head>, <body>, scripts, global fragments)
└── layout/<variant>/skeleton.html  (theme-specific slots: header, styles, body wrapper)
    └── ui/base_page.html           (page shell: dispatches to template_name or fragment_name)
        └── ui/base_auth.html       (auth shell: split layout, social-login slot)
            └── per-site base_*.html  (site-specific overrides per domain)
```

## Per-skeleton slot ownership

| Block               | Owned by `base.html` | Override in skeleton.html | Override in page.html |
|---------------------|:-------------------:|:------------------------:|:---------------------:|
| `meta`              |  default            | site meta tags           | (rarely)               |
| `styles`            | `render_bundle static` | theme font overrides   | critical CSS          |
| `header`            | empty               | header / nav             | (rarely)               |
| `body`              | empty               | `<main>` wrapper          | per-page content       |
| `footer`            | empty               | per-skeleton footer       | (rarely)               |
| `extra_assets`      | empty               | site scripts              | form helpers           |
| `content`           | (N/A — set in body) | skeleton.body block       | page content           |

## Variant selection

A page picks a variant by either:

* **URL pattern**: `site.url_prefix` → variant in `configs.settings.ENV.sites.yml`.
* **Template Name**: `<page>.html` then ` extends layout/<variant>/skeleton.html`.
* **Layout override**: caller passes `layout_path="auth/skeleton.html"` to swap.

## Migration cookbook

When adding a new site (e.g. CRM), the minimum steps are:

1. Drop `applications/<site>/assets/templates/base_<variant>.html` extending the right skeleton.
2. Set `WEBSITE_VARIANT = "<variant>"` in `applications/<site>/settings.py`.
3. Add `docs/websites/<site>/index.md` listing the variants in use.

See `docs/architecture/templates_sections.md` next for analyzer-trackable section markers.
