# CTC Research — Documentation Index

> **Canonical product path:** `projects/precis/precis-ctc/`
> **Runtime identity:** `precis-ctc` · **Public identity:** `ctc-research.com`
> **Dispatcher aliases:** `WEBSITE=ctc`, `WEBSITE=precis-ctc`, `WEBSITE=ctc-website`, `WEBSITE=ctc-research.com`
> **Main docs:** [`docs/precis-ctc/`](../../../../docs/precis-ctc/README.md)

<!-- AI-generated: review needed -->

This directory is the **project docs project** for the standalone medical
research center site. It is the single source for product-level documentation.

## 📚 Project Docs

| Doc | Covers |
|-----|--------|
| [Setup & Build](SETUP_AND_BUILD.md) | Step-by-step setup and build |
| [Contents](CONTENTS.md) | Content map and site contents |
| [Components](COMPONENTS.md) | Component registry and frontend components |
| [Templates](TEMPLATES.md) | Template architecture |
| [Environment](ENVIRONMENT.md) | Environment variables, redeploy, asset release order |
| [Enhancements](ENHANCEMENTS.md) | Enhancement register |
| [Learning Cases](LEARNING_CASES.md) | Learning cases & techniques |
| [Media Archive](MEDIA_ARCHIVE.md) | Media archive layout |

## 🔒 Startup Strategy

- [CTC Research market strategy](../../../../docs/startup/precis-ctc.md) — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog
- [Full portfolio strategy](../../../../docs/startup/STRATEGY.md) — consolidated master

## 🔗 Related

- [Main docs — CTC Research](../../../../docs/precis-ctc/README.md) — reader-facing docs incl. content strategy & publishing
- [django-fusion](../../../../libs/django-fusion/README.md) — shared framework used by this product

## 🔐 Admin & CMS access

| URL | Serves | Notes |
|-----|--------|-------|
| `https://ctc-research.com/admin/` | **Wagtail admin** | Content editing: pages, images, settings |
| `https://ctc-research.com/django-admin/` | **Django admin (Unfold)** | System/registry admin |

- Both routes are proxy-backed to the Django backend; `/admin` and
  `/django-admin` (without the trailing slash) 301 via Django `APPEND_SLASH`.
  The Traefik router matches the exact `Path()` forms so the Astro catch-all
  never intercepts them (see `../../../application/proxy/configs/traefik/dynamic/ctc-research.yml`).
- A superuser (`admin`) is seeded; credentials live in the deployment secret
  store — never commit them.

## Remarks & Notes

- The filesystem path `projects/precis/precis-ctc/` is canonical; do not create
  new code under historical paths such as `projects/precis-ctc/`.
- Public medical, legal, image-rights, and translation content requires CTC
  owner review before production publication.