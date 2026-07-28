# Tinker

> **Related Code**
> * **Domain:** Site (Tinker sandbox / experimentation surface)
> * **Paths:**
>   * `applications/tinker/www/` (Django root)
>   * `applications/tinker/settings.py` (`WEBSITE_NAME='tinker'`, `WEBSITE_IDENTIFIER='tinker'`)
>   * `applications/tinker/docker-compose.yml`
>   * `applications/tinker/DEPLOYMENT_STATUS.md` (deployment log)
> * **Production URL:** https://tinker.structa.cloud
> * **Variant:** `layout/landing/skeleton.html`

## What this site is

Tinker is the experimentation surface for prototyping new wagtail blocks, components, and RoutableComponent patterns before promoting them to the canonical LMS sites (ctc-research, lms-demo) — see [`../shared_lms.md`](../shared_lms.md).

## Site / Application / Viewset tree

```text
TinkerSite (Site)
├── SandboxApp (Application)
│   ├── BlockPreview (FragmentComponent)  -- /sandbox/blocks/
│   └── PagePreview (RoutableComponent)   -- /sandbox/pages/<slug>/
└── ShowcaseApp (Application)
    └── DemoComponent (FragmentComponent)
```

## Conventions

1. Every Tinker RoutableComponent ships in dev, graduates to staging via the deployment status log.
2. Templates root at `applications/tinker/www/templates/<page>/main.html`.

## See also

* [`prompts.md`](prompts.md) — Tinker-specific AI prompt catalog.
* [`../architecture/routable_applications.md`](../architecture/routable_applications.md) — Application class.
