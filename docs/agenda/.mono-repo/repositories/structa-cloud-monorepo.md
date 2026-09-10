---
Object type: Repository
Tags: repository, monorepo, structa-cloud
Status: Active
Type: Monorepo
Related Projects: loop-crm-merge, formint-editions-chain, ctc-research-platform, django-fusion-library, docs-agenda-system
Related Libraries: django-fusion-module
---

# structa.cloud — Monorepo

> **Description:** The single repository containing all Structa Cloud products, shared libraries, infrastructure, and documentation.

## Structure

| Path | Contents |
|---|---|
| `projects/` | Precis (precis-main, precis-landing, precis-ctc), Syntara, Formints editions, Loop-CRM |
| `libs/` | django-fusion (shared Django/Wagtail framework) |
| `application/` | Databases, proxy (Traefik/Nginx), tools (Blinko, Docus, Coder…), Compose |
| `docs/` | Docus docs, agenda system, plans, AR content |
| `tests/` | Workspace integration, HTTP, browser tests |
| `.github/` | CI workflows + composite actions |

## Boundaries

- `projects/Makefile` is the canonical dispatcher (`WEBSITE=…` targets)
- Name rules: `precis-lms` merged into `precis-main`; `syntara` replaces `cypercloud` paths; `formint-*` canonical edition names

## Related

- → `../modules/django-fusion-module.md` — Shared library
- → `../plans/projects.md` — Project directory
- → `../../../overview.md` — Repo overview (docs)
- → `../objects/repository.md` — Repository object type