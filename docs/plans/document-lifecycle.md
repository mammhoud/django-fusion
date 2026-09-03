# Documentation Lifecycle & Cleanup Plan

> **Status:** Active
> **Updated:** 2026-08-04
> **Owner:** Documentation and Product team
> **Scope:** `docs/`, especially `docs/plans/`

## Purpose

Keep documentation easy to trust. Every document must have one of four clear states:

| State | Meaning | Action |
|---|---|---|
| **Current** | Authoritative for an approved product, architecture, or workflow | Maintain and link from an index |
| **Update needed** | Useful content whose ownership, links, status, or facts are stale | Assign an owner and update before reuse |
| **Historical / archive** | No longer current but valuable for decisions, migrations, audits, or rollback | Make read-only, label clearly, and preserve |
| **Deletion candidate** | Duplicate, empty, unsupported, or fully replaced with no retention need | Quarantine first; delete only after the gate |

A document is never considered dead solely because it is old. It is dead when it has no current owner, no unique information, no active references, no audit/rollback value, and a verified replacement.

## Canonical ownership

| Content | Canonical location | Role |
|---|---|---|
| Engineering implementation, migrations, tests, dependencies, deployment | `docs/plans/` | Concise object with methods and use cases |
| Product scope, edition boundaries, market research, decisions | `docs/plans/editions/` | Knowledge-graph object and relations |
| Product source code | Project directories | Evidence linked from plans |
| Historical implementation and completed work | git history (deleted after supersession) | Recoverable evidence; never current scope |
| Marketing claims | `docs/plans/marketing-claims.md` | Approved claim summary only |

The detailed repository plan remains authoritative for implementation. Plan copies must not silently invent completion or duplicate source code.

## Current POS truth

| Document | Status | Decision |
|---|---|---|
| `docs/plans/editions/README.md` | Current (canonical) | Formints edition chain 01–08 — the main, latest product + engineering plans |

The former `docs/Anytype/` knowledge-graph docs moved to `docs/agenda/mono-repo/`
in the monorepo consolidation; product scope and market research also live
alongside the canonical plans in `docs/plans/editions/`.

The retired `docs/plans/pos/`, `docs/plans/migrated/`, `docs/plans/cms-fusion/`, and `docs/plans/precis-lms/` plan directories were deleted on 2026-08-14 (superseded by `editions/` and Precis/Precis Landing); see the deletion manifest.

## Status evidence rules

- **Complete:** implementation, tests, documentation, and release evidence exist.
- **Active:** work or maintenance is currently authorized and has an owner.
- **Planned:** approved direction without implementation evidence.
- **Superseded:** replaced by a named canonical document; keep a redirect or archive notice.
- **Archived:** read-only historical source with a replacement and retention reason.
- **Deletion candidate:** only after the deletion gate below.

Never mark a source plan complete because a newer plan describes the same work. Mark it superseded or archived and preserve unique migration evidence.

## Safe archive and deletion workflow

### 1. Inventory

Record every candidate in a deletion manifest with:

- path and document title;
- lifecycle state and reason;
- canonical replacement;
- owner and review date;
- inbound links and references;
- content hash and archive path;
- legal/compliance hold status;
- rollback test result.

### 2. Quarantine before deletion

Move or copy the candidate to a versioned archive outside the active index. Add a header:

```markdown
> **ARCHIVED:** This document is historical and is not an active source of truth.
> **Replacement:** `path/to/current-document.md`
> **Reason:** Superseded / duplicate / completed migration
> **Rollback:** See `docs/plans/deletion-manifest.md` entry `<ID>`.
```

For a first pass, prefer git history or a separately backed-up archive. Do not remove files in place as the first action.

### 3. Validate

Before deletion, run:

- repository-wide Markdown link and frontmatter checks;
- `rg` import, route, template, asset, CI, and documentation-reference scans;
- focused tests/builds for the affected product;
- Anytype import/index checks;
- a restore test from the archive;
- a marketing-claim review if the file is customer-facing.

### 4. Delete atomically

Only when the manifest is approved:

- delete one small batch at a time;
- record the deletion commit or change identifier;
- retain the archive and manifest for the retention window;
- update every index and replacement link;
- publish a changelog entry for user-facing documentation changes.

### 5. Roll back

If a missing reference, migration issue, or incorrect claim is found:

1. stop further deletion;
2. restore the archive to its original path or restore the deletion commit;
3. run the focused validation again;
4. update the manifest with the failure and corrected replacement;
5. keep the document archived until the new gate passes.

A deletion is not complete until restoration has been tested successfully.

## Holds that block deletion

Do not delete documents that describe unresolved migrations, historical architecture decisions, security incidents, financial/compliance obligations, customer commitments, or an active legal/audit hold. Mark them `Historical / archive` instead.

## Marketing tone and benefits

Marketing should communicate operational benefits without overstating evidence:

| Feature | Responsible benefit language |
|---|---|
| Offline operation | “Keep serving during connectivity interruptions; reconcile when connected.” |
| KDS | “Help kitchen teams see, prioritize, and complete tickets faster.” Do not claim a speed multiplier without a measured study. |
| Arabic-first UX | “Designed for Arabic, RTL, local invoice presentation, and bilingual workflows.” Do not claim regulatory compliance without verification. |
| Multi-branch | “Give operators a shared view of branches and controlled publishing.” Do not imply real-time guarantees until measured. |
| Loyalty | “Build repeat-visit relationships with an auditable rewards ledger.” Avoid guaranteed retention or revenue claims. |
| API access | “Provide a versioned integration path without database access.” State rate limits and supported resources. |
| Self-hosted → SaaS | “Start with local control and add managed cloud services when needed.” |

Use “planned,” “pilot,” or “available in the current release” precisely. Avoid unsupported terms such as “best,” “revolutionary,” “production-ready,” “zero downtime,” “fully compliant,” or “market leader.”

## Required claims register

Every objective marketing claim belongs in `docs/plans/marketing-claims.md` with its evidence, limitation, owner, confidence, and review date. A claim must be substantiated before publication, not after a campaign launches.

## Review cadence

- Current plans: review each release or monthly during active migration.
- Planned plans: review quarterly or when assumptions change.
- Historical archives: review only when a migration, audit, or rollback needs them.
- Claims: review before publication and at every pricing/release change.

## Related

- → `README.md` — Repository plan index
- → `marketing-claims.md` — Claims register
- → `deletion-manifest.md` — Removal register
