# CTC Research — Content Strategy, ICP & Market Research

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public site:** `ctc-research.com`
> **Audience:** academic medical researchers, clinicians who teach, research-adjacent teams, and institutions.

<!-- AI-generated: review needed -->

## Bottom line

CTC Research sells **evidence and research capability**, not software. Content
should be split into three pillars that map directly onto the product surface
already shipped (courses, publications, services). The recommended starting
plan is 3 pillars × 10 seed topics, publishing one piece per week, with every
piece routed through the `## Production notes` workflow in
[`publishing-and-production.md`](publishing-and-production.md).

Confidence tags below follow the content-strategy convention:
🟢 verified from the codebase · 🟡 reasonable inference · 🔴 assumption that
needs CTC subject-matter review before publication.

---

## 1. Ideal Customer Profiles (ICP)

Four personas. Content must stay evidence-led and never imply clinical advice.

| Persona | Who they are | Job-to-be-done | Content they need | Confidence |
|---|---|---|---|---|
| **Early-career researcher** | PhD/postdoc building a first protocol | Design a defensible study and write it up | Methods explainers, protocol templates, worked publication examples | 🟡 |
| **Clinician-educator** | Physician/health professional who teaches | Turn clinical work into teachable material | Course catalog, module/lesson previews, CME-style outcomes | 🟡 |
| **Research team lead / PI** | Runs a lab or trial program | Stand up evidence pipelines and train staff | Services, analytics, collaboration, team onboarding | 🟡 |
| **Institution / program buyer** | Department, training program, or institute | License a coherent research curriculum | Pricing, catalog, outcomes, compliance, i18n coverage | 🔴 |

**ICP dilution warning:** do not write one piece for all four. Assign each
topic to exactly one persona, and put the persona in the brief.

---

## 2. Market research (positioning snapshot)

> 🟡/🔴 — directional only. Treat the competitor claims below as assumptions
> to verify before citing them in public copy.

| Dimension | Observation | Implication |
|---|---|---|
| **Category** | Research-methods education + evidence services, not a generic LMS | Avoid "online courses" positioning; lead with research workflow |
| **Differentiator** | A research-center site with a **publication/document library** + a **localized medical curriculum** in one product | Publish the methods, then the courses — the library is the moat |
| **Adjacent competitors** | Academic LMS platforms, publisher CME libraries, freelance research-writing services | Most competitors are either *content-only* or *platform-only*; few own both |
| **Content gap** | Clear, protocol-level "how to run a study" guidance in 6+ languages | i18n is a real, defensible gap to target |
| **Trust gate** | Medical/legal claims require expert review | Every public claim needs a review gate (see publishing doc) |

**Primary keyword families (to validate):** "medical research methods",
"how to write a research protocol", "systematic review tutorial",
"clinical research training", "research publication guide".

---

## 3. Content pillars

| Pillar | Rationale | Maps to product |
|---|---|---|
| **1. Research methods** | Core search demand; builds authority | Publications library (`/documents/`), blog |
| **2. Learning & curriculum** | Converts readers into enrolled learners | Courses (`/courses/`), modules/lessons |
| **3. Evidence & outcomes** | Shareable proof; drives referrals | Services, testimonials, stats, events |

---

## 4. Priority topics (10 seed topics)

| # | Topic (working title) | Type | Keyword / angle | Pillar | Persona | Searchable / Shareable |
|---|---|---|---|---|---|---|
| 1 | How to write a research protocol: a step-by-step guide | Guide | "how to write a research protocol" | Methods | Early-career researcher | 🟢 Searchable |
| 2 | Systematic review vs scoping review: which fits your question | Comparison | "systematic review vs scoping review" | Methods | Early-career researcher | 🟢 Searchable |
| 3 | Designing a study: population, exposure, outcome | Explainer | "design a clinical study" | Methods | Early-career researcher | 🟢 Searchable |
| 4 | From clinical question to teachable module | Thought leadership | curriculum design | Learning | Clinician-educator | 🟡 Shareable |
| 5 | What we learned teaching research methods in 6 languages | Case study (original data) | i18n research education | Learning | Institution | 🟡 Shareable |
| 6 | Reading a paper critically: a 10-minute checklist | Checklist | "how to read a research paper" | Methods | Clinician-educator | 🟢 Searchable |
| 7 | Publication ethics for first-time authors | Guide | "publication ethics" | Methods | Early-career researcher | 🟢 Searchable |
| 8 | Building an evidence pipeline for a research team | Use-case | research operations | Evidence | Team lead | 🟡 Both |
| 9 | Choosing a medical research training program | Buyer's guide | "research training program" | Learning | Institution | 🟡 Searchable |
| 10 | Course outcomes: measured progress, not just certificates | Proof point | learning outcomes | Evidence | Institution | 🟡 Shareable |

---

## 5. Topic cluster map

```text
Research methods (pillar 1)
├─ How to write a research protocol (1)
│   ├─ Systematic vs scoping review (2)
│   └─ Publication ethics (7)
├─ Designing a study (3)
└─ Reading a paper critically (6)

Learning & curriculum (pillar 2)
├─ From clinical question to teachable module (4)
├─ Choosing a research training program (9)
└─ Teaching methods in 6 languages (5)

Evidence & outcomes (pillar 3)
├─ Building an evidence pipeline (8)
└─ Course outcomes proof (10)
```

Internal linking rule: pillar-1 guides link **down** to the matching course;
course pages link **up** to the methods guide that justifies them; outcomes
pieces link **across** to services and testimonials.

---

## 6. Publishing calendar (starter)

| Week | Piece | Owner (role) | Review gate |
|---|---|---|---|
| 1 | #1 Research protocol guide | Content producer | Medical review |
| 2 | #3 Designing a study | Content producer | Medical review |
| 3 | #2 Systematic vs scoping | Content producer | Editorial |
| 4 | #6 Reading a paper checklist | Clinician-educator | Medical review |
| 5 | #4 Clinical question → module | Content producer | Editorial |
| 6 | #7 Publication ethics | Content producer | Legal + medical |
| 7 | #9 Choosing a program | Marketing | CTC owner |
| 8 | #5 i18n teaching case study | Marketing | CTC owner |
| 9 | #8 Evidence pipeline | Team lead | CTC owner |
| 10 | #10 Outcomes proof | Marketing | CTC owner |

---

## Remarks & Notes

- This document is **direction, not clinical or legal copy.** Every public
  claim must pass the review gates in
  [`publishing-and-production.md`](publishing-and-production.md) before release.
- All four personas and the competitive positioning are assumptions until a CTC
  subject-matter owner confirms them; do not quote this file as validated
  market research.
- The public page map and medical-content rules (no invented statistics, no
  clinical-advice implication, label educational material) are in
  [`../../projects/precis/precis-ctc/docs/CONTENTS.md`](../../projects/precis/precis-ctc/docs/CONTENTS.md)
  and override anything here that conflicts.
- Keyword volumes are not yet validated — run the topic-cluster and keyword
  validation passes before committing budget to a pillar.
