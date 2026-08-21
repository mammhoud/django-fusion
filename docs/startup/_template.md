---
title: Startup Strategy Template
description: Template for per-product market strategy documents — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog.
navigation:
  title: Template
  icon: i-lucide-file-pen-line
object:
  type: "template"
  id: "docs.startup.template"
attributes:
  source_path: "startup/_template.md"
  canonical_route: "/docs/en/startup/_template"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - template
  - strategy
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
---

# 📋 Product Strategy Template

> Copy this file to `startup/<product>.md` and fill every section. Do not skip
> sections — a blank section is a signal for the research backlog.
>
> Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption (research needed)

## 1. Market Strategy

- **Positioning statement** (one sentence): For _[audience]_ who _[need]_, _[product]_ is a _[category]_ that _[key benefit]_.
- **Wedge** — the narrow first market we win before expanding.
- **Go-to-market** — channels, motion (PLG / sales-led / partner), sequence.
- **Moat** — defensibility: network effects, data, switching costs, IP.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | Top 1–3 problems, with evidence |
| **Solution** | How the product solves each problem |
| **Key metrics** | North-star + guardrail metrics |
| **Unfair advantage** | Why us, why now |
| **Channels** | Where customers come from |
| **Revenue model** | Pricing, packaging, billing |
| **Cost structure** | Build/run costs, margins |
| **Timeline** | MVP → first paying customer → scale |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Total addressable | $X | 🟡/🔴 | ... |
| SAM | Serviceable available | $Y | 🟡 | ... |
| SOM | Serviceable obtainable (year 3) | $Z | 🔴 | ... |

> **SOM logic:** SAM × (realistic capture rate given sales capacity) — state the capture-rate assumption.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| ... | ... | ... | 🟢 live / 🟡 beta / 🔴 planned |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| ... | ... | ... | ... | ... |

## 6. Competitive Landscape

> Who else plays in this market, how we compare, and the wedge we defend.
> Names are public-market facts; size/positioning claims carry confidence tags.

### 6.1 Competitor map

| Competitor | Category | Target | Strengths | Our edge / gap |
|-----------|----------|--------|-----------|----------------|
| ... | ... | ... | ... | ... |

### 6.2 Positioning vs. alternatives

| Dimension | Us | Direct competitors | Indirect substitutes |
|-----------|----|--------------------|---------------------|
| Deployment | Self-hosted (one Compose stack) | SaaS multi-tenant | Spreadsheets/status quo |
| Data ownership | Customer DB | Vendor-hosted | None |
| Price posture | License + services | Per-seat SaaS | Free/status quo |
| Differentiator | Shared django-fusion foundation across products | Single-product vendors | Manual workflows |

## 7. Research Needed

- [ ] _Open question 1_ — what we need to learn, who to ask, how to validate.
- [ ] _Open question 2_ — ...

> **Citation status:** competitor names are public-market facts. Market-size
> figures are directional (🟡/🔴) until verified against a named public report;
> upgrade each tag to 🟢 only with a citation.

## Remarks & Notes

- Template version: keep the section order stable so automation can diff product docs against this template.
- Update the confidence tags as research lands — 🔴 → 🟡 → 🟢.
- Never store customer-identifying data here; personas are composites.
