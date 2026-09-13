---
title: Portfolio (Resume Builder) — Feature Tracking
description: Legacy feature lifecycle entries for the resume-builder product, kept for reference only
navigation:
  title: Portfolio (Legacy)
  icon: i-lucide-id-card
object:
  type: "guide"
  id: "agenda.feature-tracking.portfolio"
attributes:
  source_path: "agenda/feature-tracking/portfolio.md"
  canonical_route: "/docs/en/agenda/feature-tracking/portfolio"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "archived"
tags:
  - structa-cloud
  - feature-tracking
  - portfolio
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Portfolio (Resume Builder) — Feature Tracking

> **Legacy:** Legacy planning (2026-08-31) for a resume-builder product; `projects/portfolio` is not an active product path in the current checkout. Entries kept for reference only — no active work links here. Do not add new features to this section.
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## P1 — Next Up (Q4 2026)

**ATS-Optimized Export**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Resume formats optimized for Applicant Tracking Systems — increases job application success.

**Scope:** ATS-compatible export formats (PDF, DOCX), formatting rules, section ordering.

**Out of scope:** ATS scoring/analysis, multiple resume versions.

**Acceptance criteria:**
- [ ] PDF export ATS-compatible
- [ ] DOCX export ATS-compatible
- [ ] Standard section ordering
- [ ] Keyword optimization hints

**Notes:** Core portfolio feature.

---

**Cover Letter Builder**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** AI-assisted cover letter generation — paired with resume for complete application.

**Scope:** Cover letter template, AI generation from resume + job description, editing.

**Out of scope:** Multiple language cover letters, video cover letters.

**Acceptance criteria:**
- [ ] Cover letter templates
- [ ] AI generates from resume + job description
- [ ] Editable output
- [ ] Export to PDF

**Notes:** Paired with resume export.

---

**Portfolio Gallery**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Image/video portfolio sections — showcase work visually.

**Scope:** Gallery section type, image/video upload, cropping, lightbox.

**Out of scope:** Video transcoding, gallery analytics.

**Acceptance criteria:**
- [ ] Image upload to portfolio
- [ ] Video upload to portfolio
- [ ] Cropping/editing
- [ ] Lightbox display

**Notes:** Visual portfolio feature.

---

**Custom Domains**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Custom domain mapping for portfolio pages — professional presence.

**Scope:** Domain configuration, DNS setup guide, SSL provisioning, domain verification.

**Out of scope:** Multiple domains per portfolio, subdomain wildcard.

**Acceptance criteria:**
- [ ] Custom domain configurable
- [ ] DNS setup instructions
- [ ] SSL automatically provisioned
- [ ] Domain verification

**Notes:** Professional feature.

---

## P2 — Planned (Q1 2027)

**Job Board Integration**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | ATS-Optimized Export |

**Why it matters:** Auto-apply with stored resume data — saves time on applications.

**Scope:** Job board API integration, auto-fill from resume, application tracking.

**Out of scope:** Multiple job board support, application analytics.

**Acceptance criteria:**
- [ ] Job listings displayed
- [ ] Auto-fill application from resume
- [ ] Application status tracked

**Notes:** Depends on ATS-Optimized Export for resume data.

---

**Analytics Dashboard**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Profile views, download counts — understand portfolio performance.

**Scope:** View tracking, download counting, analytics dashboard, time range filters.

**Out of scope:** geographic analytics, referral source tracking.

**Acceptance criteria:**
- [ ] Profile views counted
- [ ] Resume downloads counted
- [ ] Analytics dashboard
- [ ] Time range filters

**Notes:** Analytics feature.

---

**Multi-language Resumes**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Resume in multiple languages — international job applications.

**Scope:** Multi-language resume model, translation workflow, language switching.

**Out of scope:** Automated translation.

**Acceptance criteria:**
- [ ] Multiple language versions per resume
- [ ] Translation workflow
- [ ] Language switching on portfolio

**Notes:** Internationalization feature.

---

**LinkedIn Import**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Portfolio |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Auto-populate from LinkedIn profile — reduces data entry friction.

**Scope:** LinkedIn OAuth, profile data import, field mapping, sync.

**Out of scope:** LinkedIn job applications, LinkedIn messaging.

**Acceptance criteria:**
- [ ] LinkedIn OAuth connection
- [ ] Profile data imported
- [ ] Fields mapped to resume sections
- [ ] Manual sync available

**Notes:** Import feature.

---

## Remarks & Notes

- Legacy section — do not add new features here; `projects/portfolio` is not an active product path
- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
