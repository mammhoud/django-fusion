# Formint POS Dead-Code Baseline

> **Status:** Baseline started; no deletion approved
> **Date:** 2026-08-04
> **Scope:** `projects/pos/`

## Purpose

This is the initial inventory required before consolidating POS Solo, POS Full, Forge, and the new Formint boundary. It is not a deletion list. Every candidate requires static references, dynamic/template references, runtime coverage, replacement evidence, archive location, and rollback review.

## Current source boundaries

| Boundary | Classification | Action |
|---|---|---|
| `pos-solo/` | Active legacy parity source | Preserve; accept legacy identifiers |
| `pos-full/` | Active migration source | Freeze new product scope; preserve build/install path |
| `forge-pos/` | UI/feature source | Port selected behavior; keep until evidence passes |
| `pos-cloud/` | Cloud source | Keep cloud-only tenant and transport behavior |
| `formint-pos/` | Current Phase 1 boundary | Build side-by-side; no destructive replacement |
| `pos-client/` | Separate client/source candidate | Audit ownership before consolidation |
| `pos-e2e/` | Shared E2E coverage | Preserve until Formint coverage replaces it |

## Candidate classes

### Migrate then remove

- Backend full-page/layout and skeleton responses once Astro-owned targets pass.
- Duplicate React/Fusion bridges after an equivalent HTMX data section is covered.
- Duplicate assets after canonical `formint-pos/assets/` imports and visual tests pass.
- Legacy product branding in active routes after compatibility aliases are tested.

### Keep compatibility

- Database migrations and persisted identifiers.
- Sync event schemas, API routes, release scripts, and fixtures.
- POS Full and Solo build/install paths until retirement gates pass.
- E2E tests until equivalent Formint browser coverage passes.

### Archive

- Forge UI status/design evidence after Formint transfer records are complete.
- Historical Solo/Full product descriptions after current edition docs link replacements.

## Phase 1 evidence still required

- Full route/component/asset inventory.
- Frontend Astro check/build/test.
- Backend Django check and HTMX contract tests.
- Offline and sync compatibility tests.
- Restore drill from the external POS archive.
- Machine-readable asset usage report.
- Approved deletion-manifest entries before any removal.

## Rule

No file is “dead” solely because it is old, complete, duplicated by name, or not found by static analysis. Dynamic template tags, URL names, migrations, plugins, release scripts, and rollback procedures must be checked first.
