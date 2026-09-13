---
title: Precis (precis-main) — Feature Tracking
description: Feature lifecycle for the unified Precis product — LMS courses, enrollment, progress, and the merged marketing shell
navigation:
  title: Precis (precis-main)
  icon: i-lucide-graduation-cap
object:
  type: "guide"
  id: "agenda.feature-tracking.precis-main"
attributes:
  source_path: "agenda/feature-tracking/precis-main.md"
  canonical_route: "/docs/en/agenda/feature-tracking/precis-main"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - precis
  - lms
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Precis (precis-main) — Feature Tracking

> **Product history:** Was "LMS (Learning Management System)" — renamed 2026-09-10 after the precis-landing + precis-lms merge into `projects/precis/precis-main/`.
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## ✅ Shipped — Core Platform

**Unified Precis platform (LMS + landing merge)**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Precis (LMS) |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** One product instead of two: courses, enrollment, progress, and profile run on a shared backend with the marketing/catalog shell in front.

**Scope:** Wagtail content/pages, LMS backend (courses/enrollment/progress/profile), django-fusion routing, Astro marketing shell.

**Acceptance criteria:**
- [x] Courses, enrollment, and progress served from the unified backend
- [x] Marketing/catalog shell renders from the same product
- [x] django-fusion routing in place

**Notes:** Backend implemented per the 2026-09-06 truth table in [`dev-team-plans.md`](../dev-team-plans.md); deployment/CI gates and builder/data surfaces remain open work below.

---

## P1 — Next Up (Q4 2026)

**Video Hosting**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Integrated video upload + streaming for course content — essential for modern e-learning.

**Scope:** Video upload, streaming playback, course-video linking, storage management.

**Out of scope:** Live streaming (tracked separately), video editing.

**Acceptance criteria:**
- [ ] Videos uploadable to courses
- [ ] Streaming playback in course player
- [ ] Video linked to course sections
- [ ] Storage quotas managed

**Notes:** Core LMS feature, enables rich course content.

---

**Quizzes & Assessments**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Multiple choice, coding challenges, auto-grading — assessment is fundamental to learning.

**Scope:** Quiz model, question types (multiple choice, coding), auto-grading engine, result tracking.

**Out of scope:** Peer grading, manual grading UI.

**Acceptance criteria:**
- [ ] Multiple choice questions supported
- [ ] Coding challenges with auto-grading
- [ ] Quiz results tracked per student
- [ ] Pass/fail thresholds configurable

**Notes:** Core LMS feature.

---

**Progress Tracking**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Per-student progress dashboard with completion % — students and instructors need visibility.

**Scope:** Progress model, completion tracking, student dashboard, instructor overview.

**Out of scope:** Detailed analytics, progress export.

**Acceptance criteria:**
- [ ] Per-student progress tracked
- [ ] Completion % calculated
- [ ] Student dashboard shows progress
- [ ] Instructor overview available

**Notes:** Core LMS feature.

---

**Certificate Designer**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Drag-and-drop certificate template builder — certificates are a key LMS deliverable.

**Scope:** Template designer, variable fields (name, course, date), PDF generation, awarding logic.

**Out of scope:** Certificate verification API, blockchain certificates.

**Acceptance criteria:**
- [ ] Drag-and-drop template designer
- [ ] Variable fields: name, course, date
- [ ] PDF generation from template
- [ ] Certificates awarded on course completion

**Notes:** Core LMS feature.

---

**Email Automation**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Drip email sequences for course enrollment — engagement and retention.

**Scope:** Email sequence model, trigger conditions, email templates, delivery tracking.

**Out of scope:** General newsletter system, A/B testing.

**Acceptance criteria:**
- [ ] Email sequences configurable
- [ ] Triggers: enrollment, course start, reminders
- [ ] Email templates editable
- [ ] Delivery tracking

**Notes:** Engagement feature.

---

## P2 — Planned (Q1 2027)

**Live Classes**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | Video Hosting |

**Why it matters:** WebRTC-based live video sessions — real-time teaching capability.

**Scope:** WebRTC integration, session scheduling, participant management, recording.

**Out of scope:** Live chat (separate feature), breakout rooms.

**Acceptance criteria:**
- [ ] Live sessions schedulable
- [ ] WebRTC video/audio works
- [ ] Participants can join
- [ ] Sessions can be recorded

**Notes:** Depends on Video Hosting infrastructure.

---

**Discussion Forums**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Per-course discussion boards — peer learning and Q&A.

**Scope:** Forum model, thread/reply structure, course association, moderation.

**Out of scope:** Real-time chat, anonymous posting.

**Acceptance criteria:**
- [ ] Forums per course
- [ ] Threads and replies
- [ ] Instructor moderation
- [ ] Notifications for replies

**Notes:** Community feature.

---

**Peer Review**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | Quizzes & Assessments |

**Why it matters:** Student peer assessment workflows — scalable assessment for large courses.

**Scope:** Peer review assignment, rubric model, review submission, reviewer matching.

**Out of scope:** Automated peer review quality checks.

**Acceptance criteria:**
- [ ] Assignments can require peer review
- [ ] Rubrics configurable
- [ ] Reviews submitted by students
- [ ] Reviewers matched to submissions

**Notes:** Depends on Quizzes & Assessments for assessment infrastructure.

---

**Gamification**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | Progress Tracking |

**Why it matters:** Badges, leaderboards, XP points — motivation and engagement.

**Scope:** Badge model, points system, leaderboard, achievement triggers.

**Out of scope:** Team challenges, virtual currency.

**Acceptance criteria:**
- [ ] Badges definable and awardable
- [ ] XP points for activities
- [ ] Leaderboard per course
- [ ] Achievement triggers configured

**Notes:** Depends on Progress Tracking for activity data.

---

**API Integration**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** LMS as API for embedding in other platforms — extensibility.

**Scope:** REST API for courses, enrollments, progress; API key management.

**Out of scope:** GraphQL, real-time API.

**Acceptance criteria:**
- [ ] Courses API
- [ ] Enrollments API
- [ ] Progress API
- [ ] API key authentication

**Notes:** Extensibility feature.

---

## P3 — Backlog

**SCORM/xAPI**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Industry-standard e-learning content interoperability — compatibility with existing content libraries.

**Scope:** SCORM package import, xAPI statement tracking, compliance reporting.

**Out of scope:** SCORM authoring tools.

**Acceptance criteria:**
- [ ] SCORM packages importable
- [ ] xAPI statements tracked
- [ ] Compliance reports available

**Notes:** Standards compliance feature.

---

**Multi-language Courses**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Course content in multiple languages with translation management — global reach.

**Scope:** Multi-language content model, translation workflow, language switching.

**Out of scope:** Automated translation, voice-over.

**Acceptance criteria:**
- [ ] Courses have multiple language versions
- [ ] Translation workflow
- [ ] Language switching in course player

**Notes:** Internationalization feature.

---

**White-label**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P3 |
| **Product** | Precis (LMS) |
| **Owner** | TBD |
| **Target** | Backlog |
| **Depends on** | — |

**Why it matters:** Custom branding per organization — B2B flexibility.

**Scope:** Organization branding, logo, colors, custom domain.

**Out of scope:** Full CSS customization, mobile app branding.

**Acceptance criteria:**
- [ ] Organization logo configurable
- [ ] Brand colors configurable
- [ ] Custom domain supported

**Notes:** B2B tier feature.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
