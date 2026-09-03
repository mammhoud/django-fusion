# django-fusion Documentation Index (DF-000)

> **Source of truth.** This index never marks a doc "✅ Exists" until its
> file is actually present in `docs/`. Cross-references in other docs use
> the `DF-0NN` IDs in this table.

## Documentation Map

| ID | File | Topic | Status |
|----|------|-------|--------|
| DF-000 | [`docs/INDEX.md`](./INDEX.md) | This index | ✅ Exists |
| DF-001 | [`docs/01-getting-started.md`](./01-getting-started.md) | Getting started & installation | ✅ Exists |
| DF-002 | [`docs/02-architecture.md`](./02-architecture.md) | System architecture + Mermaid diagram | ✅ Exists |
| DF-003 | [`docs/03-component-system.md`](./03-component-system.md) | Component system (Python side) | ✅ Exists |
| DF-004 | [`docs/04-component-tag.md`](./04-component-tag.md) | `{% comp %}` template tag (renamed from COMPONENT_TAG.md) | ✅ Exists |
| DF-005 | [`docs/05-routing.md`](./05-routing.md) | URL routing & viewsets | ✅ Exists |
| DF-006 | [`docs/06-forms-and-tables.md`](./06-forms-and-tables.md) | Forms & tables integration (deep reference) | ✅ Exists |
| DF-007 | [`docs/07-configuration.md`](./07-configuration.md) | Settings, Dynaconf, cache backends | ✅ Exists |
| DF-008 | [`docs/08-api-reference.md`](./08-api-reference.md) | API reference (generated from docstrings) | ✅ Exists |
| DF-009 | [`docs/09-health.md`](./09-health.md) | Health checks + Docker/Kubernetes probes | ✅ Exists |
| DF-010 | [`docs/10-wagtail-integration.md`](./10-wagtail-integration.md) | Wagtail blocks, snippets, viewsets | ✅ Exists |
| DF-011 | [`docs/11-best-practices.md`](./11-best-practices.md) | Patterns mined from COMPONENT_CASE_STUDIES | ✅ Exists |
| DF-012 | [`docs/12-integration-examples.md`](./12-integration-examples.md) | End-to-end walkthroughs | ✅ Exists |
| DF-013 | [`docs/13-troubleshooting.md`](./13-troubleshooting.md) | Symptom → cause → fix entries | ✅ Exists |
| DF-014 | [`docs/14-faq.md`](./14-faq.md) | FAQ mined from real test edge cases | ✅ Exists |
| DF-015 | [`docs/15-viewflow-mapping.md`](./15-viewflow-mapping.md) | django-material → django-fusion mapping (renamed from VIEWFLOW_MAPPING.md) | ✅ Exists |
| DF-016 | [`docs/16-assets.md`](./16-assets.md) | Assets pipeline — API endpoints, template tags, Next.js integration | ✅ Exists |
| DF-017 | [`docs/17-integration-modes.md`](./17-integration-modes.md) | Webpack/template/API modes, health/media boundaries, project organization, enhancement plan | ✅ Exists |
| DF-018 | [`docs/18-render-contract.md`](./18-render-contract.md) | Slot & prop render contract (0.5.0 breaking changes): single-render slots, bare-context-var props, kwarg-style defaults, migration examples | ✅ Exists |
| DF-019 | [`docs/19-openapi-and-filtering.md`](./19-openapi-and-filtering.md) | OpenAPI docs (`OpenAPISpec`, `/docs`, `/docs/openapi.json`) + viewset filtering/search/ordering/pagination, mapped from django-bolt | ✅ Exists |
| DF-020 | [`docs/20-language-contract.md`](./20-language-contract.md) | Shared language/locale contract — resolution, persistence, middleware, API, Wagtail content selection, Mermaid diagrams | ✅ Exists |
| DF-021 | [`docs/21-landing-builder.md`](./21-landing-builder.md) | Landing builder — Wagtail page assembly from the fu-* catalog, theme picking, dynamic fields, JSON road | ✅ Exists |
| DF-022 | [`docs/22-template-fields.md`](./22-template-fields.md) | Sandboxed dynamic template field engine — parse/resolve/validate/escape/filter/preview | ✅ Exists |

## Auxiliary files (unchanged or supporting)

| File | Topic | Status |
|------|-------|--------|
| [`docs/00-package-guide.md`](./00-package-guide.md) | Complete package guide — layout, consumers, dev workflow, docs map | ✅ Exists |
| [`docs/COMPONENT_CASE_STUDIES.md`](./COMPONENT_CASE_STUDIES.md) | Per-component case studies (kept as long-form reference) | ✅ Exists |
| [`docs/legacy/django-grep-legacy/django-grep-overview.md`](./legacy/django-grep-legacy/django-grep-overview.md) | Deprecated django-grep overview | ✅ Exists — historical only |

## Conventions

- **Doc IDs:** `DF-NNN` for docs, `PR-NN` for prompts (see
  [`../PROMPTS.md`](../PROMPTS.md)). Both must remain stable across
  filename changes; if a doc is renamed, edit its row in this table.
- **Cross-link discipline:** When a doc references another doc, use the
  `DF-NNN` ID and a markdown link. Plain filename references drift.
- **Status update rule:** Switch a row from 🟡 TODO to ✅ Exists **only
  after** the file is on disk and contains real (non-stub) content.
  Stubbing `lorem ipsum` to flip a row is the exact failure mode that
  motivated this rewrite.
- **Source mapping:** Every code block in a `DF-NNN` doc should be
  traceable to a real path under `src/django_fusion/`. Comments above
  code blocks noting the source path are encouraged.

## How to add a new doc

1. Pick the next free `DF-NNN` from this table (or use `PR-NN` for prompts).
2. Create the file under `docs/` (matching numbered convention).
3. Add a row above with `Status: 🟡 TODO`.
4. Write the content with concrete examples sourced from `src/django_fusion/`.
5. Flip the row to `✅ Exists` and commit.

## How this index replaced `DOCUMENTATION_MAP.md`

The previous `docs/DOCUMENTATION_MAP.md` self-certified ~25 docs as
"✅ Complete" while ~20 of them did not exist. That file is removed; this
index is now the only navigation surface. The legacy file was the
primary motivating problem for the v0.2.0 documentation pass.
