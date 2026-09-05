---
Object type: Project
Tags: project, ctc, research, precis, wagtail
Status: Active
Related Workspace: workspace
Related Products: ctc-research
Related Teams: product, engineering
Related Plans: project-workspace
---

# CTC Research Platform — Research Center Site

> **Description:** The medical research center site (`projects/precis/precis-ctc/`) — Wagtail CMS, LMS-style courses, research profiles, newsletter, and publishing workflows.

## Outcome

A published research center presence: profile pages, courses/learning, research content, newsletter opt-in/confirm/unsubscribe, and localized content with EN/AR parity.

## Scope and gates

- In scope: Wagtail pages + StreamFields, learning modules, profile views, newsletter service, fixtures, compose deployment.
- Out of scope: unified Precis LMS product (lives in `precis-main`).
- Completion evidence: `make check`/`make test` green, fixture content verified, ceptor-ai imports fully removed (✅ COMPLETE 2026-08-16).

## Related

- → `../plans/_index.md` — Delivery plans
- → `../../feature-tracking.md` § CTC Research — ceptor-ai migration milestone
- → `../objects/project.md` — Project object type