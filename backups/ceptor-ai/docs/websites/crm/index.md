# CRM

> **Related Code**
> * **Domain:** Site (CRM / Relationship management)
> * **Paths:**
>   * `applications/crm/www/` (Django root)
>   * `applications/crm/settings.py` (`WEBSITE_NAME='crm'`, `WEBSITE_IDENTIFIER='crm'`)
>   * `applications/crm/docker-compose.yml`
>   * `applications/crm/PROJECT_DESIGN.md` (read first)
> * **Production URL:** https://crm.structa.cloud
> * **Variant:** `layout/landing/skeleton.html`

## What this site is

The CRM is the relationship-management surface for Structa Cloud. It is a CMS-leaning site built on the same `Site` / `Application` / `Viewset` routing hierarchy as VResume — see [`../architecture/routable_site.md`](../architecture/routable_site.md).

## Site / Application / Viewset tree

```text
CRMSite (Site)
├── AccountsApp (Application)
│   ├── CompanyList (RoutableComponent)   -- /accounts/companies/
│   └── ContactDetail (RoutableComponent) -- /accounts/contacts/<int:id>/
├── DealsApp (Application)
│   ├── PipelineComponent (FragmentComponent)
│   └── DealDetail (RoutableComponent)    -- /deals/<int:id>/
└── ReportsApp (Application)
    └── DashboardComponent (FragmentComponent)
```

## Conventions

1. WAGTAIL-driven Page models live in `applications/crm/www/<page>/models.py`.
2. Routable components live in `applications/crm/www/pages/routable_components.py`.
3. Site-specific template overrides root at `applications/crm/www/templates/<page>/main.html`.

## See also

* [`prompts.md`](prompts.md) — CRM-specific prompt catalog.
* [`../architecture/routable_applications.md`](../architecture/routable_applications.md) — Application layer.
* [`../architecture/routable_site.md`](../architecture/routable_site.md) — Site registration.
