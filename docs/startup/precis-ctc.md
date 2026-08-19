---
title: CTC Research — Market Strategy 🔒
description: Private strategy for CTC Research — market strategy, MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog.
navigation:
  title: CTC strategy 🔒
  icon: i-lucide-heart-pulse
object:
  type: "private-strategy"
  id: "docs.startup.precis-ctc"
attributes:
  source_path: "startup/precis-ctc.md"
  canonical_route: "/docs/en/startup/precis-ctc"
  source_of_truth: "repository-markdown"
  owner: "precis-ctc"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - precis-ctc
  - research
  - healthcare
  - publishing
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "CTC product docs"
    to: "/docs/en/precis-ctc"
    icon: "i-lucide-heart-pulse"
---

# 🏥 CTC Research — Market Strategy 🔒

> Private · Owner: `precis-ctc` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Market Strategy

- **Positioning:** For medical research centers and institutes that need credible digital presence, **CTC Research** is the research-center publishing platform that turns studies, team pages, and publications into a maintained, bilingual (EN/AR) institutional website — not a brochure, but a research communication engine.
- **Wedge:** The **research publishing workflow** — content strategy, publication pipelines, and production governance — as a repeatable product, not a one-off agency build.
- **Go-to-market:** Direct institutional sales + publishing-agency partnerships; the live ctc-research.com deployment is the reference case.
- **Moat:** Deep vertical templates (research centers), bilingual content pipeline, and publishing/production tooling that generic agencies don't have.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | Research centers have outdated, static sites; studies and team output are under-published; EN/AR parity is hard to maintain |
| **Solution** | Django/Wagtail site + Astro frontend with content strategy, publishing pipelines, and production checks (see `docs/precis-ctc/`) |
| **Key metrics** | Publications published/mo, site traffic, citation/visibility growth, content freshness |
| **Unfair advantage** | Vertical research-center domain knowledge + repeatable content strategy playbook |
| **Channels** | Direct outreach to institute comms leads; agency partnership for build-out |
| **Revenue model** | Site license/retainer + content-services subscription |
| **Cost structure** | Low infra; content services are the cost center and the margin driver |
| **Timeline** | MVP site ✅ live → 2–3 reference institutes → productized "research publishing" service |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global medical research center websites & digital presence | ~$4–6B (healthcare web/digital services) | 🔴 | Derived from healthcare digital spend |
| SAM | Research institutes & medical centers in MENA/GCC needing EN/AR research publishing | ~$80–150M | 🔴 | Segment assumption |
| SOM | Year-3: 10–25 institute engagements | ~$1–2M | 🔴 | Sales capacity-bound |

> **SOM logic:** services-led; each engagement $40–80k. Validate pipeline capacity for 10+ deals/yr.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Research site platform | Institutional site + CMS | License + hosting retainer | 🟢 (live site) |
| Publishing services | Content strategy, editorial pipeline, production | Monthly retainer | 🟢 (in-house) |
| Bilingual enablement | EN/AR content ops + RTL QA | Setup + per-article | 🟡 beta |
| Visibility & reporting | Traffic/impact analytics for institutes | Included / add-on | 🔴 planned |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Institute comms director | Runs comms for a research center | Outdated site, no publishing cadence | Funding/grant cycle needs visibility | $20–60k/yr |
| Research ops lead | Manages publications & team output | Scattered outputs, no EN/AR parity | New accreditation or grant round | $10–30k/yr |
| Agency (health vertical) | Builds sites for medical clients | Needs repeatable research-center capability | New healthcare client RFP | White-label fees |

## 6. Research Needed

- [ ] Survey 10 research centers (MENA/EU) on digital publishing pain and budget.
- [ ] Quantify the EN/AR parity cost saving — the wedge needs a defensible number.
- [ ] Competitive scan: institutional website vendors (e.g., Quartzy-adjacent, university CMS providers).
- [ ] Validate pricing for publishing retainer vs one-off build.
- [ ] Define the "research publishing pipeline" product boundary — where does the service become software?

## Remarks & Notes

- The live deployment (ctc-research.com) is both product and proof — keep it exemplary.
- Content strategy is the differentiator; the site is the shell. Sell the workflow, not the theme.
- Market sizes here are 🔴 assumptions; upgrade only with cited research.
