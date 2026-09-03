---
Object type: Feature
Tags: integration, sync, crm, payments, cloud, pos
Status: In Development
Edition: Community, Formint Professional, POS Cloud
Related Features: pos-system, pos-offline
---

# Integrations — Connectivity & External Systems

> **Type:** Feature ✨
> **Description:** All integration points for the POS suite — internal system connectivity, cloud/SaaS services, and external business systems (CRM, payments, accounting).

---

## Overview

Integrations span three layers:

| Layer | Scope | Editions |
|-------|-------|----------|
| **Internal connectivity** | Frontend ↔ sidecar ↔ database, branch sync | All editions with sync |
| **Cloud services** | CRM sync, payments, analytics, backups, multi-branch hub | Formint Professional, POS Cloud |
| **External systems** | CRM, payment gateways, accounting, email, SMS | Formint Professional, POS Cloud |

---

## Internal connectivity

| Integration | Source | Target | Protocol |
|-------------|--------|--------|----------|
| Frontend ↔ Sidecar | Tauri React UI | Python Robyn server | HTTP REST (port 8766) |
| Sidecar ↔ Database | Django ORM | SQLite / PostgreSQL | Django models |
| Solo ↔ Master | Branch device | Master server | HTTP poll |
| Full ↔ Cloud | Branch device | Cloud API | HTTPS + WebSocket |

---

## Cloud services

| Service | Integration | Benefit |
|---------|-------------|---------|
| **Cloud CRM** | Customer profile sync across all branches | Unified customer view |
| **Payment Gateway** | Stripe/Square/PayPal checkout processing | Online and in-person payments |
| **Analytics Service** | Revenue reports, sales trends, inventory forecasting | Business intelligence |
| **Cloud Backup** | Automated database backup to cloud storage | Disaster recovery |
| **Multi-Branch Sync** | Centralized data hub for all restaurant locations | Chain management |

---

## External systems

| System | Integration Type | Status |
|--------|-----------------|--------|
| **CRM** | Customer data sync — create/update contacts from sales | Planned |
| **Payments** | Stripe, Square, PayPal payment gateway integration | Planned |
| **Accounting** | QuickBooks, Xero invoice/transaction export | Planned |
| **Email** | Transactional emails — receipts, invoices, notifications | Planned |
| **SMS** | Order status updates, promotional messaging | Planned |

---

## Integration boundaries

- **Config cascade** — settings resolve site → admin → defaults before reaching an external service.
- **Auth** — API tokens per integration; cloud endpoints use HTTPS + JWT.
- **Sync** — Local service continuity is separated from cloud analytics (see `../architecture/sync-data.md`).

---

## Related Docs

- → `custom-form.md` — Form builder for CRM data collection
- → `../architecture/sync-data.md` — Synchronization boundaries
- → `../plans/cloud.md` — Cloud operating model
- → `../README.md` — Master index