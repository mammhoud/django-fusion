---
Object type: Edition
Tags: edition, formint, professional, pos, django, wagtail
Status: Completed
Related Features: pos-system, pos-offline, pos-integration, pos-cloud-integrations
Related Plans: formint-pos-professional-plan
---

# Formint Professional — Restaurant Operations Platform

> **Description:** The commercial offline-capable restaurant operations edition — Astro 5 + Alpine + HTMX frontend with a **required Django backend** (django-fusion + Unfold admin), merged from `pos-full` + `pos-solo`.

## Scope

- Everything in Standard
- Restaurant workflows: KDS, catalog, inventory, reports
- Multi-branch management, offline operation with idempotent sync, permissions, transfers
- QR menu (versioned localized menus), loyalty system
- django-fusion components, fragments, and tables
- Integrations: webhooks, email/Slack, exports

## Boundaries

- Pro is the first edition with a required Django backend
- Workspace-scoped models use `app_label = "pos_full"`, `db_table = "full_<name>"`, sync-tracking fields

## Evidence

- ✅ Done (per `docs/plans/editions/` chain status)
- `make check`/`make test` green (backend + frontend)
- Plans: `../../../plans/editions/03-pro.md`, `../../../plans/formints/formint-pro/` plans

## Related

- → `formint-standard.md` — Base tier
- → `formint-cloud.md` — Next tier (hosted SaaS)
- → `../plans/formint-pos-professional-plan.md` — Delivery contract
- → `../objects/edition.md` — Edition object type