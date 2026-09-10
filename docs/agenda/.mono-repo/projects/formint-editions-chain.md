---
Object type: Project
Tags: project, formint, pos, editions, chain
Status: Active
Related Workspace: workspace
Related Products: formint-pos
Related Teams: engineering
Related Plans: formint-pos-professional-plan
---

# Formint Editions Chain — Community → Client

> **Description:** The Formints POS extension chain: Community (Rust/Diesel/SQLite) → Standard → Pro (Django) → Cloud (multi-tenant master) → Client (Vue/Django shop), each tier adding capabilities on the previous one.

## Outcome

Every edition the docs and landing site claim actually exists, is tested, and has a canonical plan in `docs/plans/editions/`.

## Scope and gates

- In scope: per-edition plans `01-community` … `10-formint-audit`, edition chain design, comparison matrix.
- Out of scope: retired `projects/pos/` paths and legacy `formintA/B/C` labels (migration labels only).
- Completion evidence: Community ✅ done · Standard ✅ done · Pro ✅ done · Cloud 🟡 staging · Client 🔵 dev · per-edition `make check`/`make test`.

## Related

- → `../editions/_index.md` — Edition objects
- → `../plans/formint-pos-professional-plan.md` — Pro delivery contract
- → `../../../plans/editions/README.md` — Canonical editions plan index
- → `../objects/project.md` — Project object type