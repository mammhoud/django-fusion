# Precis documentation duplicate register

> **Purpose:** prevent repeated procedures and stale path references.
> **Canonical docs root:** `projects/precis/docs/`

<!-- AI-generated: review needed -->

## Source-of-truth policy

| Subject | Edit this file/tree | Do not create a second copy in |
|---|---|---|
| Precis unified runtime setup/build | `projects/precis/docs/precis-main/SETUP_AND_BUILD.md` | `precis-landing/docs/`, root docs copies |
| CTC runtime setup/build/redeploy | `projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md` and `ENVIRONMENT.md` | unrelated Precis or generic setup pages |
| CTC page/content map | `projects/precis/docs/precis-ctc/CONTENTS.md` | repeated page inventories in strategy docs |
| Precis Landing compatibility | `projects/precis/docs/precis-landing/README.md` | a new active product guide under the legacy copy |
| Cross-product architecture | `docs/ARCHITECTURE.md` and `projects/precis/docs/RELATIONSHIPS.md` | product-local copies of the whole monorepo map |
| Public product overview | `docs/precis/README.md` | implementation-level copies of all project docs |
| Startup strategy | `docs/startup/precis.md` | product README copies of market sizing and research backlog |

## Consolidated or intentionally retained material

### Retained legacy copy

`projects/precis/precis-landing/` is retained because the repository and
runtime aliases still refer to it. Its docs now live in
`projects/precis/docs/precis-landing/` and explicitly point to the unified
Precis docs where content is shared.

### Public mirror versus implementation docs

`docs/precis/` and `docs/precis-ctc/` are reader-facing navigation and strategy
surfaces. They link to the implementation source under this directory. They
should not repeat environment tables, component inventories, or full build
procedures.

### Historical plans

Migration and publish plans under `docs/plans/` remain historical decision
records. They may mention the path that existed when the plan was written, but
active links must point to the current `projects/precis/docs/` locations.

## Migration rules

1. Search the central tree before creating a new product guide.
2. Add a link or subsection when the information is already owned elsewhere.
3. Mark historical material as historical; do not present it as an active command.
4. Update relative links whenever a product docs path changes.
5. Do not remove a retained compatibility document without checking runtime
   aliases and existing references.

## Remarks & Notes

- Duplicate content is not the same as duplicate runtime code; this register covers documentation ownership only.
- The retained Precis Landing copy is a compatibility boundary, not an invitation to fork the unified product docs.
- Review this register when a product is renamed, merged, or moved again.
