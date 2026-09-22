---
title: CTC Research — Sample Project (Agentic Coding with Precis) 🔒
description: Sample record for CTC Research — a medical research center site built with agentic coding on the Precis stack; market strategy, MVP canvas, and research kept as reference material.
navigation:
  title: CTC sample 🔒
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
  - sample
  - agentic-coding
  - research
  - healthcare
  - publishing
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "CTC product docs"
    to: "/precis-ctc"
    icon: "i-lucide-heart-pulse"
  - label: "Content strategy"
    to: "/precis-ctc/content-strategy"
    icon: "i-lucide-pen-tool"
  - label: "Publishing workflow"
    to: "/precis-ctc/publishing-and-production"
    icon: "i-lucide-send"
---

# 🏥 CTC Research — Sample Project (Agentic Coding with Precis) 🔒

> Private · Owner: `precis-ctc` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

> ## 🧪 Sample status — not a commercial product
>
> **CTC Research** (`projects/precis/precis-ctc/`) is a **sample project built
> with agentic coding on the Precis stack** — a live medical research center
> site (ctc-research.com) demonstrating the Precis platform, EN/AR publishing,
> and the production workflow. It is **not offered as a product**; the market
> strategy, MVP canvas, and research below are retained as reference material
> for the 🔬 Precis Research vision and for teams using Precis + agentic coding
> to build similar sites. See the
> [client production case study](../precis-ctc/client-production.md).
>
> Editorial planning belongs in the [content strategy](../precis-ctc/content-strategy.md),
> and release operations belong in the [publishing workflow](../precis-ctc/publishing-and-production.md).

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

## 5. Commercial ICP

The commercial ICP is intentionally kept in this strategy document so pricing,
market sizing, and buying triggers have one source of truth. Editorial reader
segments and content-to-conversion paths live in the [content strategy](../precis-ctc/content-strategy.md).

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Institute comms director | Runs comms for a research center | Outdated site, no publishing cadence | Funding/grant cycle needs visibility | $20–60k/yr |
| Research ops lead | Manages publications & team output | Scattered outputs, no EN/AR parity | New accreditation or grant round | $10–30k/yr |
| Agency (health vertical) | Builds sites for medical clients | Needs repeatable research-center capability | New healthcare client RFP | White-label fees |

## 6. Competitive Landscape

> Names are public-market facts; size/positioning claims carry confidence tags.

### 6.1 Competitor map

| Competitor | Category | Target | Strengths | Our edge / gap |
|-----------|----------|--------|-----------|----------------|
| Silverchair | Scholarly publishing platform | Publishers & societies | Journal hosting, peer-review integrations, domain authority | Journal-centric; we target the research-center *institutional site* (teams, studies, publications, EN/AR) |
| Atypon (Literatum) | Publishing platform | Publishers & libraries | Large-scale journal platforms | Same — enterprise journal infrastructure, not research-center websites |
| University/health web agencies | Custom website build | Universities, hospitals, institutes | Design, brand, custom features | One-off builds with no publishing workflow; we productize the workflow |
| WordPress/Wagtail agencies | CMS builds | Any organization | Cheap, flexible | Same — no research-publishing domain playbook or EN/AR pipeline |
| Quartzy / lab-management suites | Lab operations | Research labs | Lab inventory/ops | Adjacent (operations, not digital presence/publishing) — not a direct competitor |

### 6.2 Positioning vs. alternatives

| Dimension | Us | Direct competitors | Indirect substitutes |
|-----------|----|--------------------|---------------------|
| Deployment | Self-hosted Django/Wagtail + Astro frontend | Agency one-off builds | Static brochure sites |
| Workflow | Research publishing pipeline (production, EN/AR parity, checks) | Agencies without a repeatable workflow | PDF/print-first publishing |
| Price posture | License + publishing retainer | Six-figure agency builds | In-house webmasters |
| Differentiator | Vertical research-center domain knowledge + content strategy playbook | Generic web vendors | Spreadsheets/static pages |

> **Gaps to attack (🟡):** citation/visibility analytics as a sellable add-on, RTL-first content ops for Arabic centers, and a published “research publishing” case study from the live ctc-research.com deployment.

## 7. Research Needed

- [ ] Survey 10 research centers (MENA/EU) on digital publishing pain and budget.
- [ ] Quantify the EN/AR parity cost saving — the wedge needs a defensible number.
- [ ] Formalize the Silverchair/Atypon boundary: when does a center graduate to a journal platform?
- [ ] Validate pricing for publishing retainer vs one-off build.
- [ ] Define the "research publishing pipeline" product boundary — where does the service become software?

> **Citation status:** competitor names are public-market facts. Market-size figures are directional (🟡/🔴) until verified against a named public report.

## Remarks & Notes

- The live deployment (ctc-research.com) is both product and proof — keep it exemplary.
- Content strategy is the differentiator; the site is the shell. Sell the workflow, not the theme.
- Market sizes here are 🔴 assumptions; upgrade only with cited research.
