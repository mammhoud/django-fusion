---
title: Marketing Plans
description: Marketing plans, positioning, launch campaigns, and evidence-backed claims
navigation:
  title: Marketing Plans
  icon: i-lucide-megaphone
---

# 📢 Marketing Plans

> **Scope:** Product positioning, launch campaigns, content strategy, and evidence-backed marketing claims across Structa Cloud products
> **Canonical Source:** `docs/plans/marketing-claims.md` → Marketing Claims Register
> **Updated:** 2026-08-25

---

## 🎯 Core Positioning Principles

### Lead with Customer Outcomes
- **Fewer service interruptions** — offline-first architecture
- **Clearer kitchen coordination** — KDS routing & prioritization
- **Easier Arabic and bilingual service** — RTL-first, localized invoices
- **Controlled branch operations** — multi-branch permissions & publishing
- **Traceable customer rewards** — auditable loyalty ledger
- **Safer integrations** — versioned API, no direct DB access
- **Migration path preserving local control** — local-to-cloud transition

### Avoid Selling Technology Lists
Tauri, Django, Astro, HTMX, cloud transport are **supporting details**; the marketing story is **continuity, clarity, control, and measurable restaurant outcomes**.

---

## 📋 Approved Claims & Evidence Status

| Claim | Product | Audience | Evidence Level | Status | Review Date |
|-------|---------|----------|----------------|--------|-------------|
| Arabic-first | Formint (all) | MENA operators | Capability → Pilot needed | In progress | 2026-Q4 |
| Offline-first | Community, Pro | Unstable connectivity | Pilot (3 restaurants) | In progress | 2026-Q4 |
| KDS routing | Pro, Cloud | Restaurant operators | Capability | Planned | 2026-Q1 |
| Multi-branch | Cloud | Chains/franchises | Capability | Planned | 2026-Q1 |
| Loyalty ledger | Pro, Cloud | Customer-focused | Capability | Planned | 2026-Q2 |
| API access | Cloud | Partners/developers | Capability | Planned | 2026-Q2 |
| Local-to-cloud | All editions | Growing operators | Pilot (migration) | Planned | Quarterly |

---

## 🚀 Launch Campaigns by Product

### Formint Community (✅ Launched)
- **Position:** "Offline-first POS for independent restaurants"
- **Channels:** GitHub, Rust/Tauri communities, restaurant forums
- **Assets:** Demo video, README, screenshots, installation guide
- **Status:** Live — iterate based on user feedback

### Formint Standard (✅ Launched)
- **Position:** "Community + advanced features for growing restaurants"
- **Differentiation:** Additional features over Community
- **Status:** Live — document feature parity

### Formint Professional (🔄 Pre-Launch)
- **Target:** Restaurants needing cloud sync + Django admin
- **Key Messages:** Sidecar sync, Unfold admin, multi-terminal
- **Launch Gates:**
  - [ ] Django backend stable
  - [ ] Sync reliability > 99.9%
  - [ ] Unfold admin configured
  - [ ] Pilot evidence collected
  - [ ] Documentation complete
- **Target Launch:** 2026-Q4

### Formint Cloud (📋 Planned)
- **Target:** Chains, franchises, multi-location operators
- **Key Messages:** Multi-tenant SaaS, real-time sync, Bolt dashboard, KDS
- **Launch Gates:**
  - [ ] Multi-tenancy stable
  - [ ] Channels/WebSocket scaling validated
  - [ ] Bolt dashboard feature-complete
  - [ ] KDS pilot evidence
  - [ ] Multi-branch pilot evidence
  - [ ] Arabic RTL pilot evidence
  - [ ] Compliance evidence (ZATCA, VAT)
  - [ ] Pricing validated against costs
- **Target Launch:** 2026-Q1

### Formint Client (✅ Launched)
- **Position:** "Lightweight Vue 3 + Tauri POS client for Cloud"
- **Channels:** Cloud onboarding, partner integrations
- **Status:** Live — Cloud-dependent

### Precis LMS (🔄 Active)
- **Position:** "Unified LMS + marketing catalog for learning businesses"
- **Key Messages:** Courses, enrollment, progress, certificates, catalog SEO
- **Launch Gates:**
  - [ ] Frontend build stable
  - [ ] Deployment gates passing
  - [ ] Wagtail CMS integrated
  - [ ] Catalog SEO optimized
- **Status:** Active development

### Precis Landing (✅ Live)
- **Position:** "Marketing site for Precis — catalog, SEO, lead gen"
- **Contract:** Post-only rendering (HTML/HTMX/JSON)
- **Status:** Live — content iterations ongoing

### CTC Research (🔄 Pre-Publish)
- **Position:** "Medical research center — publications, multi-lang, media"
- **Key Messages:** Research catalog, ES/SV/PT-BR, media proxy, email parity
- **Launch Gates:**
  - [ ] Content/component audit complete
  - [ ] Multi-lang catalogs (es/sv/pt-br)
  - [ ] Media bundles proxy configured
  - [ ] Email parity + test
  - [ ] `make redeploy` validated
  - [ ] Cross-module workflows documented
- **Target Publish:** 2026-Q3

### Syntara (🔄 Active)
- **Position:** "AI chat + template customizer for developers"
- **Key Messages:** Multi-provider (Ollama/OpenAI/Claude/Gemini), Monaco editor, template discovery
- **Status:** Active development — localhost/default `cypercloud.localhost`

---

## 🌐 Content Strategy

### Documentation as Marketing
- **Technical docs** → Developer trust & SEO
- **Architecture guides** → Technical buyer confidence
- **Runbooks** → Operational credibility
- **API specs** → Integration readiness signal

### Multi-Language (EN/AR Parity)
- **Required:** All customer-facing content
- **Structure:** `docs/content/en/` ↔ `docs/ar-content/`
- **Process:** Author in EN → translate to AR → review by native speaker
- **Products:** Formint (priority), Precis, CTC

### Content Types by Funnel Stage

| Stage | Content Type | Distribution |
|-------|-------------|--------------|
| **Awareness** | Blog posts, architecture guides, case studies | SEO, social, dev communities |
| **Consideration** | Product comparisons, feature deep-dives, pilot stories | Website, email, webinars |
| **Decision** | Pricing, compliance evidence, migration guides, ROI calculator | Sales calls, dedicated pages |
| **Retention** | Release notes, best practices, advanced guides, community | In-app, newsletter, forum |

---

## 📅 Marketing Calendar (High-Level)

| Quarter | Focus | Key Activities |
|---------|-------|----------------|
| **2026-Q3** | Formint Pro launch prep, CTC publish | Pilot evidence, docs, demo assets |
| **2026-Q4** | Formint Pro launch, Cloud pilot | Launch campaign, pilot recruitment |
| **2027-Q1** | Formint Cloud launch, Precis LMS polish | Multi-tenant launch, compliance showcase |
| **2027-Q2** | Cross-product integration stories | Formint↔Loop-CRM, Precis↔Formint |

---

## 🔗 Cross-References

- **Marketing Claims Register:** `docs/plans/marketing-claims.md` — authoritative claims & evidence
- **Plan Registry:** `docs/plans/README.md` — engineering plans with marketing gates
- **Recommendations:** `docs/recommendations.md` — prioritized actions
- **Formint Editions:** `docs/plans/editions/README.md` — edition positioning
- **Document Lifecycle:** `docs/plans/document-lifecycle.md` — content status & ownership
- **Project Awareness:** `docs/guides/00-project-awareness.md` — product map & commands
- **Arabic Content:** `docs/ar-content/` — AR parity source

---

## Remarks & Notes

- **Evidence first:** No claim published without documented evidence per `marketing-claims.md`
- **Arabic parity:** All customer-facing marketing content requires AR version
- **Technical accuracy:** Marketing reviews with dev leads before publication
- **Compliance:** Regulated claims (ZATCA, VAT, FTA) require legal/specialist sign-off
- **Pilot transparency:** Pilot scope, sample, limitations always disclosed
- **Git history:** Superseded marketing plans archived via deletion manifest

<!-- AI-generated: review needed -->