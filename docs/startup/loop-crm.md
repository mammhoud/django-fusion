---
title: Loop-CRM — Market Strategy 🔒
description: Private strategy for Loop-CRM — unified sales + marketing CRM. MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog.
navigation:
  title: Loop-CRM strategy 🔒
  icon: i-lucide-handshake
object:
  type: "private-strategy"
  id: "docs.startup.loop-crm"
attributes:
  source_path: "startup/loop-crm.md"
  canonical_route: "/docs/en/startup/loop-crm"
  source_of_truth: "repository-markdown"
  owner: "loop-crm"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - loop-crm
  - crm
  - saas
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Loop-CRM product docs"
    to: "/loop-crm"
    icon: "i-lucide-handshake"
---

# 🤝 Loop-CRM — Market Strategy 🔒

> Private · Owner: `projects/loop-crm/` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Market Strategy

- **Positioning:** For SMBs tired of stitching a sales CRM to a separate marketing tool, **Loop-CRM** is the unified sales + marketing platform that merges pipeline management with marketing automation (built from the Twenty + Postiz lineage) on one Django backend with Wagtail-managed landing pages.
- **Wedge:** **Pipeline + publishing in one** — sales stages, deals, activities alongside marketing landing pages and social/marketing automation, replacing two subscriptions with one.
- **Go-to-market:** Product-led: free tier for pipeline, upgrade for marketing automation; landing-page templates via Wagtail make self-serve onboarding fast.
- **Moat:** Unified data model (contacts/companies/deals/pipelines/activities) powering both sales and marketing — the integration is the product.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | SMBs run CRM + marketing as separate tools with sync breaks; costs double, data diverges |
| **Solution** | Unified CRM + marketing: pipelines, deals, contacts, activities + Wagtail landing pages + publishing flows (see `docs/loop-crm/`) |
| **Key metrics** | Deals created, pipeline velocity, landing page → lead conversion, marketing campaign ROI |
| **Unfair advantage** | Single data model across sales & marketing; self-hostable; Wagtail content power |
| **Channels** | PLG signup, landing-page template gallery, agency partners, migration tools from legacy CRMs |
| **Revenue model** | Freemium seats; paid tiers for automation, publishing, and integrations |
| **Cost structure** | Shared Django infra; marketing features add email/social delivery costs |
| **Timeline** | MVP (pipeline + landing) ✅ → marketing automation GA → paid tiers |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global CRM software market | ~$65–70B (2025) | 🟡 | Public CRM market reports |
| SAM | SMB CRM + marketing automation (EU + MENA, EN/AR) | ~$4–6B | 🔴 | Segment assumption |
| SOM | Year-3: 500–2,000 SMB teams | ~$1–3M ARR | 🔴 | PLG conversion assumptions |

> **SOM logic:** free pipeline tier → 3–6% paid conversion at $20–80/mo; needs signup telemetry to validate.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Pipeline CRM | Contacts, companies, deals, activities | Free tier → paid seats | 🟢 (product) |
| Marketing automation | Campaigns, publishing, landing pages | Paid add-on tier | 🟡 beta |
| Landing page CMS | Wagtail-managed marketing pages | Included (differentiator) | 🟢 (product) |
| Migration service | Import from Salesforce/HubSpot/legacy CRMs | One-time fee | 🔴 planned |
| Self-hosted license | Deploy Loop-CRM on own infra | License + support | 🔴 planned |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| SMB sales owner | 3–20 person sales team | CRM + marketing tool sprawl, sync breaks | Quarterly review of tool costs | $30–100/mo/seat |
| Marketing lead (SMB) | Runs campaigns + landing pages | No unified lead source | Launching a new campaign | $50–150/mo |
| Agency (growth) | Manages client pipelines + funnels | Repeatable stack for clients | New client acquisition | White-label fees |

## 6. Competitive Landscape

> Names are public-market facts; size/positioning claims carry confidence tags.

### 6.1 Competitor map

| Competitor | Category | Target | Strengths | Our edge / gap |
|-----------|----------|--------|-----------|----------------|
| HubSpot | All-in-one CRM + marketing | SMB → mid-market | Brand, ecosystem, marketing automation | Expensive per-seat tiers, vendor-hosted, data lock |
| Pipedrive | Sales pipeline CRM | Small sales teams | Pipeline UX, simplicity | Sales-only — no marketing automation/landing |
| Zoho CRM | Suite CRM | SMB | Breadth (whole Zoho suite), price | Suite sprawl, clunkier UX |
| Twenty (OSS) | Open-source CRM | Developers/SMB | Modern OSS CRM, self-host | Sales-focused; we add marketing automation on the same data model |
| Postiz (OSS) | Social publishing/scheduling | Marketers | Social scheduling breadth | Scheduling-only; we unify it with pipeline + landing |
| HighLevel | Agency CRM + funnels | Agencies | Funnels, agency white-label | Heavier, US-centric, vendor lock |
| Salesforce (SMB SKUs) | Enterprise CRM | Mid-large | Features, ecosystem | Overkill pricing/ops for SMB |

### 6.2 Positioning vs. alternatives

| Dimension | Us | Direct competitors | Indirect substitutes |
|-----------|----|--------------------|---------------------|
| Deployment | Self-hosted Django/Wagtail | SaaS (HubSpot, Pipedrive, Zoho) | Sheets + Mailchimp + calendar |
| Data model | One model powers sales + marketing + landing | Two products, sync breaks | Manual sync |
| Price posture | Freemium seats → paid automation tier | Per-seat SaaS | Free/spreadsheets |
| Differentiator | Twenty + Postiz lineage, Wagtail landing pages, self-host | Single-layer CRMs or single-layer schedulers | Status quo |

> **Gaps to attack (🟡):** the “two subscriptions → one” pitch against HubSpot/Pipedrive+Mailchimp stacks, self-hosting for data-sensitive SMBs, and EN/AR localization for MENA/GCC buyers.

## 7. Research Needed

- [ ] Validate the "two tools → one" value prop with 10 SMB interviews (pricing anchors).
- [ ] Feature-gap matrix vs HubSpot, Pipedrive, Zoho, Twenty OSS, Postiz — migration pain points.
- [ ] Measure PLG funnel (signup → paid) once telemetry ships.
- [ ] Confirm MENA/GCC CRM localization demand (Arabic RTL, VAT, integrations).
- [ ] Define marketing automation scope: email vs social publishing vs landing pages — what ships first?

> **Citation status:** competitor names are public-market facts. Market-size figures are directional (🟡/🔴) until verified against a named public report.

## Remarks & Notes

- The Twenty + Postiz lineage is a credibility asset in OSS communities — use it in developer-facing docs.
- Wagtail-managed landing pages are the visible differentiator; keep them first-class in demos.
- Sizing is 🔴 assumption-heavy; telemetry on the signup funnel is the top priority to firm it up.
