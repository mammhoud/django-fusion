---
title: Formint POS — Market Strategy 🔒
description: Private strategy for Formint POS — market strategy, MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog across all editions.
navigation:
  title: Formint strategy 🔒
  icon: i-lucide-store
object:
  type: "private-strategy"
  id: "docs.startup.formints"
attributes:
  source_path: "startup/formints.md"
  canonical_route: "/docs/en/startup/formints"
  source_of_truth: "repository-markdown"
  owner: "formints"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - formints
  - pos
  - saas
  - retail
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Formint POS product docs"
    to: "/docs/en/pos"
    icon: "i-lucide-store"
---

# 💳 Formint POS — Market Strategy 🔒

> Private · Owner: `projects/formints/` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Market Strategy

- **Positioning:** For restaurants, cafes, and gaming centers that refuse to be locked into expensive POS SaaS, **Formint** is the offline-first, multi-edition point-of-sale family — from a free community edition to a cloud-master SaaS — built on one Tauri 2 + React + Rust core with optional Django backends.
- **Wedge:** **Community → Pro → Cloud funnel**: the free desktop edition generates adoption, Pro adds the server (Django Ninja API, loyalty, sidecar), Cloud adds multi-store sync and SaaS revenue.
- **Go-to-market:** Community edition (open visibility, marketplace listings) → paid Pro upgrades → Cloud multi-store SaaS for chains; partner/reseller channel for installs.
- **Moat:** Offline-first reliability, single core across 5 editions, deep vertical features (KDS, gaming center, payroll), and a full cloud sync story competitors split across products.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | POS SaaS fees, per-terminal pricing, and online-only dependency hurt small F&B operators; existing tools don't cover gaming centers or offline-first needs |
| **Solution** | Desktop POS (SQLite, offline) + optional Django server (API, loyalty, admin) + cloud master for multi-store sync |
| **Key metrics** | Terminal activations, community→Pro conversion, cloud stores onboarded, uptime offline |
| **Unfair advantage** | One codebase, five editions; Rust + SQLite performance; full cloud sync; i18n en/fr/ar |
| **Channels** | Marketplace listings (Windows/macOS/Linux), resellers, community seed bundle, agency installers |
| **Revenue model** | Free community; paid Pro license; Cloud SaaS subscription per store |
| **Cost structure** | Desktop dev cost high, marginal server cost; support/install services |
| **Timeline** | Community ✅ → Pro ✅ → Cloud SaaS → chain rollout |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global restaurant POS / retail point-of-sale software | ~$25–35B (2025) | 🟡 | Public POS market reports |
| SAM | POS for cafes, restaurants, gaming centers (EU, MENA, FR/AR/EN markets) | ~$1.5–3B | 🔴 | Segment assumption |
| SOM | Year-3: 2,000–5,000 active terminals, 50–150 cloud stores | ~$1–4M ARR | 🔴 | Funnel from community adoption |

> **SOM logic:** community adoption base → 3–7% Pro conversion; Cloud priced per store/mo. Needs real telemetry on activations to firm up.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Community edition | Free offline desktop POS | Free (adoption wedge) | 🟢 live |
| Pro license | Server API, loyalty, KDS, payroll, admin | One-time + updates | 🟢 live |
| Cloud master (SaaS) | Multi-store sync, CRM, dashboard, cloud DB | Monthly per store | 🟢 live (Django cloud) |
| Setup & training | Installation, menu migration, staff training | Project + hourly | 🟡 beta |
| White-label / franchise | Branded POS for chains & resellers | Contract | 🔴 planned |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Cafe/restaurant owner | 1–3 terminals | POS fees, offline outages, clunky UI | Monthly fee renewal / outage | $10–50/mo/terminal |
| Gaming center operator | Multiple stations + KDS | Gaming-center features missing elsewhere | New location opening | $50–150/mo |
| Small chain ops manager | 3–20 stores | No unified multi-store reporting | Scaling to new store | $100–300/mo |
| Reseller/installer | Serves F&B clients | Repeatable POS to install | Client demand | Margin on license+install |

## 6. Research Needed

- [ ] Install telemetry on community edition to measure activations & conversion funnel (required to firm SOM).
- [ ] Competitive matrix: Square, Toast, Lightspeed, Loyverse — feature/price gaps to attack in each market.
- [ ] Validate gaming-center vertical willingness-to-pay (niche but underserved).
- [ ] Test Cloud SaaS pricing anchors (per-store vs per-terminal vs % of sales).
- [ ] Market-entry research: EU vs MENA regulatory (tax/VAT receipts, GDPR) for billing features.

## Remarks & Notes

- Edition boundaries are deliberate: do not blur Community (free, no server) and Cloud (Django master) in external messaging.
- The cloud master is Django-served today (the legacy Robyn sidecar is gone) — docs and sales materials must say "Django cloud".
- All sizing is directional; telemetry on the community funnel is the single highest-value research item.
