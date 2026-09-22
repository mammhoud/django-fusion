---
Object type: Module
Tags: module, library, ceptor-ai, ai, archived
Status: Archived
Type: Library
Related Repositories: structa-cloud-monorepo
Related Projects: ctc-research-platform
Related Documentation: _index
---

# ceptor-ai — AI Client & MCP Tooling (Archived)

> **Description:** Former AI chat client / MCP server package (`libs/ceptor-ai/`). **Removed from the checkout** — zero `ceptor_ai` imports remain under `projects/precis/` (verified 2026-08-16).

## History

- Provided AI chat client, MCP server, BEM converter, agent generation
- Consumed by Syntara (primary), django-fusion (MCP metadata), shared worker
- Replaced by native models, Wagtail blocks, and django-fusion equivalents

## Replacement

- CTC Research migrated to native models (see the ceptor-ai migration milestone)
- `libs/ceptor-ai` no longer exists in the checkout — git history is the archive

## Related

- → `../../feature-tracking/ctc-research.md` — ceptor-ai migration milestone
- → `../../case-studies/ceptor-ai.md` — Historical case study
- → `../objects/module.md` — Module object type