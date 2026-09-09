---
Object type: Recommendation
Tags: recommendation, plans, milestones, documentation
Status: Implemented
Priority: High
Impact: Medium
Effort: Low
Related Goals: documentation-goals
---

# Close Finished Plans as Milestones

> **Description:** Adopt the plans → milestones reference contract: finished plans are deleted from `docs/plans/` and recorded as ✅ Shipped milestones in the agenda.

## Rationale

- Keeps `docs/plans/` canonical and current — no dead plan files
- Git history remains the archive
- Every completed plan has a backward pointer (feature-tracking § milestone)

## Implementation

- Documented in `../../CONTENT_MODEL.md` § 4.2
- Executed for Loop-CRM closeout (3 plans), ceptor-ai migration, finish-community-standard

## Related

- → `../../CONTENT_MODEL.md` — Reference contract
- → `../../feature-tracking.md` — Milestone log
- → `../objects/recommendation.md` — Recommendation object type