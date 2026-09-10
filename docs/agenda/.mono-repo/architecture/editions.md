---
Object type: Architecture
Tags: architecture, edition, pos, formint-pos, community, professional, saas
Status: Published
Version: 2026-08
---

# POS Editions

> **Description:** Canonical boundaries for the three customer-facing POS editions.

## Edition flow

- **Community** (self-hosted core) → upgrade by capability and support
- **Formint Professional** (offline restaurant operations) → optional hosted migration
- **POS Cloud** (tenants, branches, billing, managed services)

## Comparison

| Capability | Community | Formint Professional | POS Cloud |
|---|:---:|:---:|:---:|
| Core POS, products, categories, inventory, reports | ✅ | ✅ | ✅ |
| Offline checkout | ✅ | ✅ | ✅ with local fallback |
| Multi-terminal and branch workflows | — | ✅ | ✅ |
| KDS, QR Menu, loyalty, API, mobile waiter | — | ✅ | ✅ |
| Hosted backups, billing, tenant isolation | — | Optional | ✅ |
| Central analytics and managed updates | — | Optional | ✅ |

## Responsibilities

### Community

A useful, low-barrier self-hosted edition for one small operator, evaluation, or developer. It prioritizes core sales, catalog, inventory, reports, Arabic/English foundations, and local ownership.

### Formint Professional

The commercial desktop and PWA edition for restaurants that need offline continuity, hardware integration, multi-branch workflows, KDS, QR menus, loyalty, API access, and mobile waiter operations. Astro owns the interface shell and loading states; Django and django-fusion own domain rules and lean data responses.

### POS Cloud

The hosted control plane for organizations that need tenant isolation, branch coordination, central analytics, billing, backups, managed updates, and integrations. Cloud transport decisions belong only to the cloud plan.



## Shared methods

All editions should use stable business vocabulary: organization, branch, terminal, station, menu, order, sale, customer, loyalty ledger, and sync event. The edition changes deployment and service scope, not the meaning of historical sales.

## Related

- → `../plans/formint-pos-professional-plan.md` — Formint product contract
- → `../plans/pos-market-research.md` — Edition market research
- → `../plans/cloud.md` — SaaS cloud boundary
- → `../plans/tauri-desktop.md` — Professional desktop tools
- → `../objects/edition.md` — Edition object type
