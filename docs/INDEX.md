# django-fusion Documentation Index (DF-000)

> **Source of truth.** This index never marks a doc "✅ Exists" until its file is
> actually present in `docs/`. Cross-references in other docs use the `DF-0NN`
> IDs in this table.

## Documentation map

| ID | File | Topic | Status |
|----|------|-------|--------|
| DF-000 | [`docs/INDEX.md`](./INDEX.md) | This index | ✅ Exists |
| DF-001 | [`docs/01-getting-started.md`](./01-getting-started.md) | Getting started & installation | ✅ Exists |
| DF-002 | [`docs/02-architecture.md`](./02-architecture.md) | System architecture + Mermaid diagram | ✅ Exists |
| DF-003 | [`docs/03-component-system.md`](./03-component-system.md) | Component system (Python side) | ✅ Exists |
| DF-004 | [`docs/04-component-tag.md`](./04-component-tag.md) | `{% comp %}` template tag | ✅ Exists |
| DF-005 | [`docs/05-routing.md`](./05-routing.md) | URL routing & viewsets | ✅ Exists |
| DF-006 | [`docs/06-forms-and-tables.md`](./06-forms-and-tables.md) | Forms & tables integration | ✅ Exists |
| DF-007 | [`docs/07-configuration.md`](./07-configuration.md) | Settings, Dynaconf, cache backends | ✅ Exists |
| DF-008 | [`docs/08-api-reference.md`](./08-api-reference.md) | API reference (from real docstrings) | ✅ Exists |
| DF-009 | [`docs/09-health.md`](./09-health.md) | Health checks + Docker/Kubernetes probes | ✅ Exists |
| DF-010 | [`docs/10-wagtail-integration.md`](./10-wagtail-integration.md) | Wagtail blocks, snippets, viewsets | ✅ Exists |
| DF-011 | [`docs/11-best-practices.md`](./11-best-practices.md) | Patterns mined from component case studies | ✅ Exists |
| DF-012 | [`docs/12-integration-examples.md`](./12-integration-examples.md) | End-to-end walkthroughs | ✅ Exists |
| DF-013 | [`docs/13-troubleshooting.md`](./13-troubleshooting.md) | Symptom → cause → fix entries | ✅ Exists |
| DF-014 | [`docs/14-faq.md`](./14-faq.md) | FAQ mined from real test edge cases | ✅ Exists |
| DF-015 | [`docs/15-viewflow-mapping.md`](./15-viewflow-mapping.md) | django-material → django-fusion mapping | ✅ Exists |
| DF-016 | [`docs/16-assets.md`](./16-assets.md) | Assets pipeline — API endpoints, template tags | ✅ Exists |
| DF-017 | [`docs/17-integration-modes.md`](./17-integration-modes.md) | Integration modes and project boundaries | ✅ Exists |
| DF-018 | [`docs/18-render-contract.md`](./18-render-contract.md) | Slot & prop render contract (0.5.0 breaking changes) | ✅ Exists |
| DF-019 | [`docs/19-openapi-and-filtering.md`](./19-openapi-and-filtering.md) | OpenAPI docs + viewset filtering/search/ordering | ✅ Exists |
| DF-020 | [`docs/20-language-contract.md`](./20-language-contract.md) | Shared language/locale contract | ✅ Exists |
| DF-021 | [`docs/21-landing-builder.md`](./21-landing-builder.md) | Landing builder — page assembly, themes, JSON road | ✅ Exists |
| DF-022 | [`docs/22-template-fields.md`](./22-template-fields.md) | Sandboxed dynamic template field engine | ✅ Exists |
| DF-023 | [`docs/23-publishing.md`](./23-publishing.md) | Build, validate, and publish to PyPI | ✅ Exists |

## Auxiliary files

Long-form and topic-specific references that are not part of the numbered set.

| File | Topic | Status |
|------|-------|--------|
| [`docs/00-package-guide.md`](./00-package-guide.md) | Package guide — layout, consumers, dev workflow, docs map | ✅ Exists |
| [`docs/COMPONENT_CASE_STUDIES.md`](./COMPONENT_CASE_STUDIES.md) | Per-component case studies | ✅ Exists |
| [`docs/COMPONENT_FORMS_TABLES.md`](./COMPONENT_FORMS_TABLES.md) | Forms & tables usage guide | ✅ Exists |
| [`docs/DESIGNER_MCP.md`](./DESIGNER_MCP.md) | Interactive designer MCP surface | ✅ Exists |
| [`docs/WEBSITE_MCP.md`](./WEBSITE_MCP.md) | MCP-assisted website/webapp review tools | ✅ Exists |
| [`../QUICKSTART.md`](../QUICKSTART.md) | 30-second forms & tables setup | ✅ Exists |
| [`../PROMPTS.md`](../PROMPTS.md) | `PR-NN` prompt reference for AI-assisted changes | ✅ Exists |

## Conventions

- **Doc IDs:** `DF-NNN` for docs, `PR-NN` for prompts (see
  [`../PROMPTS.md`](../PROMPTS.md)). IDs are stable across filename changes; if a
  doc is renamed, update its row here in the same change.
- **Cross-link discipline:** reference other docs by `DF-NNN` ID with a markdown
  link. Plain filename references drift.
- **Status rule:** flip a row from 🟡 TODO to ✅ Exists **only after** the file is
  on disk with real, non-stub content. Stubbing `lorem ipsum` to flip a row is the
  exact failure mode that motivated this rewrite.
- **Source mapping:** every code block in a `DF-NNN` doc should be traceable to a
  real path under `src/django_fusion/`. Note the source path above code blocks.
- **Import paths are tested:** `tests/test_documented_import_paths.py` imports the
  canonical paths the docs and README advertise. Adding a documented path means
  adding it to that list.

## How to add a new doc

1. Pick the next free `DF-NNN` from this table (or `PR-NN` for prompts).
2. Create the file under `docs/` using the numbered convention.
3. Add a row above with `Status: 🟡 TODO`.
4. Write the content with concrete examples sourced from `src/django_fusion/`.
5. Flip the row to ✅ Exists and commit.

## Related

- [README](../README.md) — install, extras, canonical imports, base-vs-customization
- [CONTRIBUTING](../CONTRIBUTING.md) — workflow, commit conventions, releasing
- [DF-023 Publishing](./23-publishing.md) — the release runbook
