---
Object type: Project
Tags: project, docs, agenda, docus, diagrams, knowledge-graph
Status: Active
Related Workspace: workspace
Related Products: documentation
Related Teams: product, engineering
Related Milestones: agenda-content-model, agenda-diagrams
---

# Docs + Agenda System — Documentation Pipeline

> **Description:** The `docs/` pipeline (Docus), the agenda system (`docs/agenda/`), the Anytype import set (`docs/agenda/mono-repo/`), the plans → milestones reference contract, and the rendered diagram package.

## Outcome

Documentation is current, de-duplicated, EN/AR parity preserved, every finished plan recorded as a ✅ Shipped milestone, and every diagram viewable as a rendered image.

## Scope and gates

- In scope: Docus content pipeline (`prepare-content`/`validate-content`), agenda (feature tracking, tasks, team notes, case studies), CONTENT_MODEL definition, diagram render script (`render-agenda-diagrams.mjs`), Anytype schema.
- Out of scope: product code changes — docs only.
- Completion evidence: `prepare-content` clean; validator warnings unchanged from baseline (532 pre-existing legacy frontmatter warnings); 59 rendered diagram SVGs resolve.

## Related

- → `../documentation/_index.md` — Documentation objects
- → `../diagrams/_index.md` — Diagram objects
- → `../../CONTENT_MODEL.md` — Agenda definition
- → `../../diagrams/README.md` — Diagram package
- → `../objects/project.md` — Project object type