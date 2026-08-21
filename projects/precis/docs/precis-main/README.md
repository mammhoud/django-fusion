# Precis (precis-main) — Documentation Index

> **Canonical product path:** `projects/precis/precis-main/`
> **Runtime identity:** `precis-main` · **Dispatcher aliases:** `WEBSITE=precis-main`, `WEBSITE=precis-lms`, `WEBSITE=precis-landing`, `WEBSITE=structa`, `WEBSITE=lms`, `WEBSITE=core`
> **Main docs:** [`docs/precis/`](../../../../docs/precis/README.md)

<!-- AI-generated: review needed -->

This directory is the **project docs project** for the unified Precis product
(LMS courses/enrollment/progress/profile merged with the landing marketing/catalog
shell). It is the single source for product-level documentation; the reader-facing
site lives in the main docs tree.

## 📚 Project Docs

| Doc | Covers |
|-----|--------|
| [Setup & Build](SETUP_AND_BUILD.md) | Unified product setup, backend + frontend build/run |
| [Catalog & Fusion](CATALOG_AND_FUSION.md) | Catalog shell + fusion rendering model |
| [Project Design](PROJECT_DESIGN.md) | Product design decisions |
| [Templates](TEMPLATES.md) | Template architecture and conventions |
| [Wagtail Render Model](WAGTAIL_RENDER_MODEL.md) | Page/StreamField render pipeline |
| [Recommendations](RECOMMENDATIONS.md) | Recommended priorities |
| [Use Cases](USECASE.md) | Product use cases |
| [ADR — Merge projects into products](adr/0001-merge-projects-into-products.md) | Architecture decision record |

## 🔒 Startup Strategy

- [Precis market strategy](../../../../docs/startup/precis.md) — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog
- [Full portfolio strategy](../../../../docs/startup/STRATEGY.md) — consolidated master

## 🔗 Related

- [Main docs — Precis](../../../../docs/precis/README.md) — reader-facing product docs
- [Legacy Precis Landing docs](../precis-landing/README.md) — kept legacy copy (only landing-specific files)
- [django-fusion](../../../../libs/django-fusion/README.md) — shared framework used by this product

## Remarks & Notes

- This directory is the canonical home for the shared Precis docs; the legacy
  `precis-landing/` copy keeps only landing-specific files and links here.
- Keep paths synchronized with the dispatcher aliases in `projects/Makefile`.