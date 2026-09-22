---
Object type: Edition
Tags: edition, precis, lms, landing, unified
Status: In Development
Related Features: intro-pages-cms, learning-curve, quizzes, custom-form
Related Plans: project-workspace
---

# Precis (Unified) — LMS + Landing Catalog Shell

> **Description:** The merged Precis product (`projects/structa.cloud/`) — LMS courses/enrollment/progress/profile merged with the landing marketing/catalog shell.

## Scope

- LMS: courses, enrollment, learning progress, learner profiles, quizzes
- Landing: marketing pages, catalog shell, intro pages CMS (Wagtail StreamFields)
- Component library + custom forms

## Boundaries

- `precis/precis-landing` is a kept legacy copy; runtime identity stays `precis-landing`
- Do not add new product code under `precis-lms` paths (merged and removed)

## Evidence

- 🟡 Active (merge in progress)
- Dispatcher: `WEBSITE=structa.cloud` (aliases `precis-lms`/`precis-landing` map to it)

## Related

- → `../features/intro-pages-cms.md` — CMS feature
- → `../features/learning-curve.md` — Learning experience
- → `../objects/edition.md` — Edition object type