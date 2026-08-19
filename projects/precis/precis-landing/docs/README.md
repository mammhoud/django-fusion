# Precis Landing-Fusion — Documentation

> **Legacy copy of the Landing-Fusion marketing site.**
> **Runtime identity:** `precis-landing` · **Canonical product:** `projects/precis/precis-main/`
> **Dispatcher aliases:** `WEBSITE=precis-landing` and `WEBSITE=precis-lms` both map to `precis-main`.

<!-- AI-generated: review needed -->

## One docs project per product

The unified Precis product (LMS + landing/marketing shell) merged the Landing-Fusion
content, so its documentation is **one shared docs project** living in
[`projects/precis/precis-main/docs/`](../../precis-main/docs/README.md). This legacy copy keeps
only the files that are genuinely landing-specific and points at the canonical docs.

## Landing-specific files (kept here)

| Document | Description |
|----------|-------------|
| **[Setup & Build](SETUP_AND_BUILD.md)** | Landing-Fusion runtime: Astro + HTMX + Alpine frontend, Django + Wagtail backend, build/run commands |

## Canonical product docs (in precis-main/docs/)

| Document | Description |
|----------|-------------|
| [Catalog & Fusion](../../precis-main/docs/CATALOG_AND_FUSION.md) | Catalog shell + fusion rendering model |
| [Project Design](../../precis-main/docs/PROJECT_DESIGN.md) | Unified product design decisions |
| [Templates](../../precis-main/docs/TEMPLATES.md) | Template architecture and conventions |
| [Wagtail Render Model](../../precis-main/docs/WAGTAIL_RENDER_MODEL.md) | Page/StreamField render pipeline |
| [Recommendations](../../precis-main/docs/RECOMMENDATIONS.md) | Recommended priorities |
| [Use Cases](../../precis-main/docs/USECASE.md) | Product use cases |
| [ADR](../../precis-main/docs/adr/) | Architecture decision records |
| [Setup & Build](../../precis-main/docs/SETUP_AND_BUILD.md) | Unified product setup/build |

## Remarks & Notes

- The six shared docs (CATALOG_AND_FUSION, PROJECT_DESIGN, TEMPLATES,
  WAGTAIL_RENDER_MODEL, RECOMMENDATIONS, USECASE) were byte-identical copies of
  the precis-main docs and were deleted here; `precis-main/docs/` is the single
  source. Edit them there.
- Do not re-copy shared docs into this directory — link to
  `../precis-main/docs/` instead.
- Per the repository map, `precis/precis-main` is the current filesystem
  location for the unified product; this directory is a kept legacy copy.